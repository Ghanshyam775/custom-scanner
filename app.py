from flask import Flask, render_template, jsonify, request
import cv2
from pyzbar.pyzbar import decode
import base64
import json
import numpy as np

app = Flask(__name__)

@app.route('/')
def scanner():
    return render_template('scanner.html')

@app.route('/decode_qr', methods=['POST'])
def decode_qr():
    try:
        # Parse JSON payload
        image_data = request.json.get('image', None)
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode Base64 image data
        image_data = base64.b64decode(image_data.split(',')[1])

        # Convert to OpenCV-compatible format
        np_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Decode QR code
        decoded_objects = decode(img)
        if not decoded_objects:
            return jsonify({"error": "No QR code detected"}), 404

        # Process the first valid QR code detected
        obj = decoded_objects[0]
        decoded_data = base64.b64decode(obj.data.decode('utf-8'))
        decoded_json = json.loads(decoded_data)

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

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON from QR code data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
