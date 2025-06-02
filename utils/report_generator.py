from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
import os
import datetime

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        ))
        
    def generate_report(self, output_path, patient_info, prediction_result, visualization_path=None):
        """Generate a PDF report with the prediction results"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        title_style = self.styles['Heading1']
        title = Paragraph("TB VISION - Tuberculosis Detection Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.25*inch))
        
        # Date and Time
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_paragraph = Paragraph(f"Report Generated: {date_time}", self.styles['Normal'])
        story.append(date_paragraph)
        story.append(Spacer(1, 0.25*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.styles['Heading2']))
        
        patient_data = [
            ["ID", patient_info.get('id', 'N/A')],
            ["Name", patient_info.get('name', 'N/A')],
            ["Age", patient_info.get('age', 'N/A')],
            ["Gender", patient_info.get('gender', 'N/A')]
        ]
        
        patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 0.25*inch))
        
        # Prediction Results
        story.append(Paragraph("Prediction Results", self.styles['Heading2']))
        
        prediction_data = [
            ["Prediction", prediction_result['prediction']],
            ["Confidence", f"{prediction_result['confidence']:.2%}"],
            ["Raw Score", f"{prediction_result['raw_score']:.4f}"]
        ]
        
        prediction_table = Table(prediction_data, colWidths=[1.5*inch, 4*inch])
        prediction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (1, 0), 
             colors.lightgreen if prediction_result['prediction'] == 'Normal' else colors.salmon)
        ]))
        
        story.append(prediction_table)
        story.append(Spacer(1, 0.25*inch))
        
        # Visualization
        if visualization_path and os.path.exists(visualization_path):
            story.append(Paragraph("X-ray Analysis Visualization", self.styles['Heading2']))
            vis_img = Image(visualization_path, width=6*inch, height=3*inch)
            story.append(vis_img)
            story.append(Spacer(1, 0.25*inch))
        
        # Disclaimer
        disclaimer_text = (
            "DISCLAIMER: This report is generated using TBVISION, a deep learning model that uses a self-trained convolutional neural network and is intended for "
            "research and educational purposes only. The predictions should not be used as the sole basis "
            "for clinical decisions. Always consult with a qualified healthcare professional for proper "
            "diagnosis and treatment. The model's accuracy is limited, and false positives/negatives can occur."
        )
        
        story.append(Paragraph(disclaimer_text, self.styles['Disclaimer']))
        
        # Build the PDF
        doc.build(story)
        return output_path