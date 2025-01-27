from flask import Flask, render_template, jsonify, request
import cv2
from pyzbar.pyzbar import decode
import base64
import json
import numpy as np
import os

app = Flask(__name__)

# Route to render the home page
@app.route('/')
def scanner():
    return render_template('index.html')

# Route to handle QR code decoding
@app.route('/decode_qr', methods=['POST'])
def decode_qr():
    try:
        # Parse the JSON payload
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode Base64 image data
        try:
            image_data = base64.b64decode(image_data.split(',')[1])
        except (IndexError, base64.binascii.Error):
            return jsonify({"error": "Invalid Base64 image data"}), 400

        # Convert to OpenCV-compatible format
        np_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Failed to process the image"}), 400

        # Decode QR code using pyzbar
        decoded_objects = decode(img)
        if not decoded_objects:
            return jsonify({"error": "No QR code detected"}), 404

        # Process the first valid QR code detected
        obj = decoded_objects[0]
        try:
            decoded_data = base64.b64decode(obj.data.decode('utf-8'))
            decoded_json = json.loads(decoded_data)
        except (json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error):
            return jsonify({"error": "Failed to decode JSON from QR code data"}), 400

        # Validate the global_id
        if decoded_json.get('global_id') != 'MY_APP_QR_CODE':
            return jsonify({"error": "Invalid QR code"}), 400

        # Return the extracted data
        return jsonify({
            "status": "success",
            "data": {
                "global_id": decoded_json.get('global_id'),
                "id": decoded_json.get('id'),
                "name": decoded_json.get('name'),
                "email": decoded_json.get('email'),
                "custom_fields": decoded_json.get('custom_fields', {})
            }
        }), 200

    except Exception as e:
        # Catch unexpected errors and return a generic message
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Entry point for the application
if __name__ == "__main__":
    # Use the PORT environment variable for deployment; default to 3000
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
