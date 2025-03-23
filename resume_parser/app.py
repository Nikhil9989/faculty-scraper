"""
Flask API for uploading and parsing resumes.

This module provides a simple API to upload resumes (PDF and DOCX)
and extract information from them.
"""

import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
from parser_factory import parse_resume

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Resume parser API is running',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.route('/upload', methods=['POST'])
def upload_resume():
    """
    Endpoint to upload a resume file (PDF or DOCX).
    
    Returns:
        JSON response with upload status and file info
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    # Check if the user submitted an empty form
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No file selected'
        }), 400
    
    # Check if the file is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': f'File type not allowed. Please upload a PDF or DOCX file.',
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # Save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    logger.info(f"Successfully uploaded file: {filename}")
    
    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'filename': filename,
        'file_path': file_path,
        'file_type': filename.rsplit('.', 1)[1].lower()
    })

@app.route('/parse', methods=['POST'])
def parse_resume_api():
    """
    Endpoint to parse a previously uploaded resume.
    
    Expects a JSON payload with the filename to parse.
    
    Returns:
        JSON response with parsed resume data
    """
    # Check if the request has the filename
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({
            'status': 'error',
            'message': 'No filename provided in the request'
        }), 400
    
    filename = secure_filename(data['filename'])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': f'File {filename} not found'
        }), 404
    
    # Check if the file type is supported
    if not allowed_file(filename):
        return jsonify({
            'status': 'error',
            'message': f'File {filename} has an unsupported format. Supported formats are: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Parse the resume
        logger.info(f"Parsing resume: {filename}")
        parsed_data = parse_resume(file_path)
        
        if 'error' in parsed_data:
            return jsonify({
                'status': 'error',
                'message': parsed_data['error']
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': parsed_data,
            'file_type': filename.rsplit('.', 1)[1].lower()
        })
    except Exception as e:
        logger.error(f"Error parsing resume {filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error parsing resume: {str(e)}'
        }), 500

@app.route('/parse-upload', methods=['POST'])
def parse_upload():
    """
    Endpoint to upload and parse a resume in one step.
    
    Returns:
        JSON response with parsed resume data
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    # Check if the user submitted an empty form
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No file selected'
        }), 400
    
    # Check if the file is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': f'File type not allowed. Please upload a PDF or DOCX file.',
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"Successfully uploaded file: {filename}")
        
        # Parse the resume
        logger.info(f"Parsing resume: {filename}")
        parsed_data = parse_resume(file_path)
        
        if 'error' in parsed_data:
            return jsonify({
                'status': 'error',
                'message': parsed_data['error']
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded and parsed successfully',
            'filename': filename,
            'file_type': filename.rsplit('.', 1)[1].lower(),
            'data': parsed_data
        })
    except Exception as e:
        logger.error(f"Error processing resume {file.filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing resume: {str(e)}'
        }), 500

@app.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Return the list of supported file formats."""
    return jsonify({
        'status': 'success',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'message': 'These file formats are supported for resume parsing'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
