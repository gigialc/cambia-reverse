from flask import Flask, render_template, request, send_file
import os
import sys
from simple_obfuscator import process_image
import tempfile
from PIL import Image
import io

app = Flask(__name__)

# Create upload and results directories if they don't exist
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy-Safe Photo Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
            .container { text-align: center; }
            .result-container { margin-top: 20px; }
            img { max-width: 100%; height: auto; margin-top: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .upload-form { 
                margin: 20px 0; 
                padding: 30px; 
                border-radius: 12px; 
                background-color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .analysis { 
                margin: 20px 0; 
                padding: 20px; 
                background-color: white; 
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .analysis-item { margin: 10px 0; }
            .success { color: #28a745; }
            .warning { color: #dc3545; }
            .info-box {
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: left;
            }
            .submit-btn {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .submit-btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Privacy-Safe Photo Generator</h1>
            <div class="info-box">
                <h3>🔒 Protect Your Privacy While Maintaining AI Verification</h3>
                <p>Upload your photo to create a privacy-safe version that:</p>
                <ul>
                    <li>✅ Remains recognizable by AI verification systems</li>
                    <li>✅ Protects your privacy from human viewing</li>
                    <li>✅ Perfect for ID verification while keeping your original photo private</li>
                </ul>
            </div>
            <div class="upload-form">
                <h2>Upload Your Photo</h2>
                <form action="/process" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept="image/*" required>
                    <br><br>
                    <input type="submit" value="Generate Privacy-Safe Photo" class="submit-btn">
                </form>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process_image_route():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # Save uploaded file
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    
    # Process with our obfuscator
    output_filename = f'processed_{file.filename}'
    output_path = os.path.join(RESULTS_FOLDER, output_filename)
    
    try:
        # Process image and get analysis
        analysis = process_image(input_path, output_path)
        
        # Determine success message based on recognition
        success_message = ""
        if any('still recognizable' in result for result in analysis['face_comparisons']):
            success_message = '''
                <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2>🎉 Perfect! Your Privacy-Safe Photo is Ready!</h2>
                    <p>Your processed photo is:</p>
                    <ul style="text-align: left;">
                        <li>✅ Successfully verified by AI recognition</li>
                        <li>✅ Protected from human viewing</li>
                        <li>✅ Ready to use for verification purposes</li>
                    </ul>
                </div>
            '''
        else:
            success_message = '''
                <div style="background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2>⚠️ Adjustment Needed</h2>
                    <p>The processed photo might be too obscured for AI verification. Try uploading a clearer photo of your face.</p>
                </div>
            '''
        
        # Return the result page with both images and analysis
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Privacy-Safe Photo Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
                .container {{ text-align: center; }}
                .image-container {{ 
                    display: flex; 
                    justify-content: space-around; 
                    margin-top: 20px;
                    background-color: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .image-box {{ flex: 1; margin: 10px; }}
                img {{ max-width: 100%; height: auto; border-radius: 8px; }}
                .back-button {{ margin-top: 20px; }}
                .back-button a {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #6c757d;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .back-button a:hover {{
                    background-color: #5a6268;
                }}
                .technical-details {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your Privacy-Safe Photo is Ready</h1>
                {success_message}
                <div class="image-container">
                    <div class="image-box">
                        <h3>Original Photo</h3>
                        <img src="/uploads/{file.filename}" alt="Original Photo">
                    </div>
                    <div class="image-box">
                        <h3>Privacy-Safe Version</h3>
                        <img src="/results/{output_filename}" alt="Privacy-Safe Photo">
                    </div>
                </div>
                <div class="technical-details">
                    <h3>Technical Verification Details</h3>
                    <p>Original Photo: {analysis['original_faces']} faces detected</p>
                    <p>Privacy-Safe Version: {analysis['processed_faces']} faces detected</p>
                    <p>AI Recognition Status: {analysis['face_comparisons'][0]}</p>
                </div>
                <div class="back-button">
                    <a href="/">← Process Another Photo</a>
                </div>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f'Error processing image: {str(e)}', 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route('/results/<filename>')
def result_file(filename):
    return send_file(os.path.join(RESULTS_FOLDER, filename))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
