import numpy as np
import tensorflow as tf
import cv2
import pywt
import matplotlib.pyplot as plt
import io
import os
from config import Config

class TBPredictor:
    def __init__(self):
        # Load the model
        self.model = tf.keras.models.load_model(Config.MODEL_PATH)
        self.img_size = (224, 224)
    
    def apply_wavelet(self, img, wavelet='db1', level=1):
        """Apply wavelet transform for image preprocessing"""
        coeffs = pywt.wavedec2(img, wavelet, level=level)
        coeffs_H = list(coeffs)
        coeffs_H[0] *= 0
        return pywt.waverec2(coeffs_H, wavelet)
    
    def preprocess_image(self, image_path):
        """Preprocess image similar to training preprocessing"""
        # Read image in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0)
        img = clahe.apply(img)
        
        # Gamma correction
        gamma = 1.2
        img = np.array(255 * (img / 255) ** gamma, dtype='uint8')
        
        # Wavelet transform
        img = self.apply_wavelet(img)
        
        # Normalization
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Resize
        img = cv2.resize(img, self.img_size)
        
        # Add channel dimension and normalize
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=-1)
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        
        return img
    
    def predict(self, image_path):
        """Make prediction on image"""
        preprocessed_img = self.preprocess_image(image_path)
        prediction = self.model.predict(preprocessed_img)[0][0]
        
        result = {
            'prediction': 'Tuberculosis' if prediction > 0.5 else 'Normal',
            'confidence': float(prediction) if prediction > 0.5 else float(1 - prediction),
            'raw_score': float(prediction)
        }
        
        return result
    
    def generate_visualization(self, image_path, save_path=None):
        """Generate visualization of model analysis"""
        # Read original image
        orig_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        orig_img = cv2.resize(orig_img, self.img_size)
        
        # Preprocess image
        preprocessed_img = self.preprocess_image(image_path)
        
        # Generate dummy heatmap for visualization (replace with actual Grad-CAM if needed)
        heatmap = np.random.rand(self.img_size[0], self.img_size[1])
        
        # Plot the image and heatmap overlay
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.imshow(orig_img, cmap='gray')
        plt.title('Original X-ray')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.imshow(orig_img, cmap='gray')
        plt.imshow(heatmap, alpha=0.6, cmap='jet')
        plt.title('Model Analysis Heatmap')
        plt.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return buf

# Optional: Install required libraries
def install_dependencies():
    try:
        import pywt
        import cv2
        import tensorflow
    except ImportError:
        print("Installing required dependencies...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
                                'PyWavelets', 'opencv-python-headless', 
                                'tensorflow', 'matplotlib'])