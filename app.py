from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import base64
import secrets
from werkzeug.security import generate_password_hash
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Generate a secure secret key for the session
app.secret_key = secrets.token_hex(32)

def save_photo(photo_data, user_id):
    """Save base64 encoded photo to disk"""
    try:
        # Remove the base64 header
        if 'base64,' in photo_data:
            photo_data = photo_data.split('base64,')[1]
        
        # Decode base64 string
        photo_bytes = base64.b64decode(photo_data)
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(UPLOAD_FOLDER, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'photo_{timestamp}.jpg'
        filepath = os.path.join(user_dir, filename)
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(photo_bytes)
        
        return True, filename
    except Exception as e:
        logger.error(f"Error saving photo: {str(e)}")
        return False, str(e)

@app.route('/upload', methods=['POST'])
def upload_photos():
    try:
        data = request.get_json()
        
        if not data or 'photos' not in data:
            return jsonify({'status': 'error', 'message': 'No photos provided'}), 400
        
        # In a real application, you would get the user_id from the session
        # For demo purposes, we'll use a dummy user_id
        user_id = 'demo_user'
        
        successful_uploads = []
        failed_uploads = []
        
        for i, photo in enumerate(data['photos']):
            success, result = save_photo(photo, user_id)
            if success:
                successful_uploads.append(result)
            else:
                failed_uploads.append(f"Photo {i+1}: {result}")
        
        response_data = {
            'status': 'success' if len(failed_uploads) == 0 else 'partial',
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in upload_photos: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/location', methods=['POST'])
def save_location():
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid location data'}), 400
        
        # In a real application, you would get the user_id from the session
        user_id = 'demo_user'
        
        # Save location to a file (in a real app, you'd typically use a database)
        user_dir = os.path.join(UPLOAD_FOLDER, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
        location_file = os.path.join(user_dir, 'location.txt')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(location_file, 'a') as f:
            f.write(f"{timestamp}: Lat {data['latitude']}, Long {data['longitude']}\n")
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error in save_location: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # In production, use a proper WSGI server instead of Flask's built-in server
    app.run(host='0.0.0.0', port=5000, debug=False)
