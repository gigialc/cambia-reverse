from flask import Flask, render_template, request, send_file, jsonify
from flask_talisman import Talisman
from werkzeug.utils import secure_filename
import os
import tempfile
import shutil
from simple_obfuscator import process_image
from PIL import Image
import io

app = Flask(__name__)
Talisman(app, content_security_policy=None)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['RESULTS_FOLDER'] = os.getenv('RESULTS_FOLDER', 'results')

# Create upload and results directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        filename = secure_filename(file.filename)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, filename)
            output_path = os.path.join(temp_dir, f'processed_{filename}')
            
            # Save and process
            file.save(input_path)
            processed_image = process_image(input_path)
            
            # Convert processed image to bytes
            img_byte_arr = io.BytesIO()
            Image.fromarray(processed_image).save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return send_file(
                img_byte_arr,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'processed_{filename}'
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'An internal server error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=False)
