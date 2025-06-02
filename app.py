import os
import uuid
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config
from utils.azure_storage import AzureStorage
from utils.prediction import TBPredictor
from utils.report_generator import PDFReportGenerator
from utils.model_downloader import initialize_app_storage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize app storage and download model
try:
    model_path = initialize_app_storage()
    logger.info(f"Using model at: {model_path}")
except Exception as e:
    logger.error(f"Failed to initialize storage: {e}")
    raise

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
azure_storage = AzureStorage()
tb_predictor = TBPredictor()
pdf_generator = PDFReportGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'xray' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['xray']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{unique_id}_{filename}"
            
            # Save locally
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
            
            # Upload to Azure Blob Storage
            blob_name = f"xrays/{new_filename}"
            azure_storage.upload_file(file_path, blob_name)
            
            # Get patient info
            patient_info = {
                'id': request.form.get('patient_id', 'Unknown'),
                'name': request.form.get('patient_name', 'Anonymous'),
                'age': request.form.get('patient_age', 'Unknown'),
                'gender': request.form.get('patient_gender', 'Unknown')
            }
            
            # Make prediction
            prediction_result = tb_predictor.predict(file_path)
            
            # Generate visualization
            viz_filename = f"viz_{new_filename}"
            viz_path = os.path.join(app.config['UPLOAD_FOLDER'], viz_filename)
            tb_predictor.generate_visualization(file_path, viz_path)
            
            # Upload visualization to Azure
            viz_blob_name = f"visualizations/{viz_filename}"
            azure_storage.upload_file(viz_path, viz_blob_name)
            
            # Generate PDF report
            report_filename = f"report_{new_filename.rsplit('.', 1)[0]}.pdf"
            report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
            pdf_generator.generate_report(report_path, patient_info, prediction_result, viz_path)
            
            # Upload report to Azure
            report_blob_name = f"reports/{report_filename}"
            azure_storage.upload_file(report_path, report_blob_name)
            
            # Store data in session for results page
            session[f'result_data_{new_filename}'] = {
                'xray_path': file_path,
                'viz_path': viz_path,
                'report_path': report_path,
                'patient_info': patient_info,
                'prediction': prediction_result,
                'filename': new_filename,
                'report_filename': report_filename
            }
            
            # Redirect to results page with the result ID
            return redirect(url_for('results', xray_id=new_filename))
        
    return render_template('upload.html')

@app.route('/results/<xray_id>')
def results(xray_id):
    # Get stored data from session
    session_key = f'result_data_{xray_id}'
    result_data = session.get(session_key)
    
    if not result_data:
        # If no session data, try to reconstruct (fallback for direct URL access)
        xray_path = os.path.join(app.config['UPLOAD_FOLDER'], xray_id)
        
        if not os.path.exists(xray_path):
            flash('X-ray not found')
            return redirect(url_for('upload'))
        
        # Fallback patient info (will show default values)
        patient_info = {
            'id': 'Unknown',
            'name': 'Anonymous',
            'age': 'Unknown',
            'gender': 'Unknown'
        }
        
        # Make prediction
        prediction_result = tb_predictor.predict(xray_path)
        
        viz_filename = f"viz_{xray_id}"
        report_filename = f"report_{xray_id.rsplit('.', 1)[0]}.pdf"
    else:
        # Use data from session
        patient_info = result_data['patient_info']
        prediction_result = result_data['prediction']
        viz_filename = f"viz_{xray_id}"
        report_filename = result_data['report_filename']
    
    # Get URLs for templates
    xray_url = url_for('static', filename=f'uploads/{xray_id}')
    viz_url = url_for('static', filename=f'uploads/{viz_filename}')
    report_url = url_for('download_report', report_name=report_filename)
    
    return render_template(
        'results.html',
        xray_url=xray_url,
        viz_url=viz_url,
        report_url=report_url,
        patient_info=patient_info,
        prediction=prediction_result
    )

@app.route('/download_report/<report_name>')
def download_report(report_name):
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_name)
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        flash('Report not found')
        return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    # Get list of all X-rays
    xray_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename) and not filename.startswith('viz_') and not filename.startswith('report_'):
            xray_files.append({
                'filename': filename,
                'url': url_for('static', filename=f'uploads/{filename}'),
                'date': datetime.fromtimestamp(os.path.getctime(
                    os.path.join(app.config['UPLOAD_FOLDER'], filename)
                )).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by date (newest first)
    xray_files.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('gallery.html', xray_files=xray_files)

@app.route('/about')
def about():
    return render_template('about.html', 
                          video_url_1=app.config['VIDEO_URL_1'],
                          video_url_2=app.config['VIDEO_URL_2'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)