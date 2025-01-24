const video = document.getElementById('video');
const captureButton = document.getElementById('capture');
const uploadButton = document.getElementById('upload');
const qrFileInput = document.getElementById('qrFile');
const resultDiv = document.getElementById('result');

// Access device camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        video.srcObject = stream;
        video.play();
    })
    .catch((err) => {
        console.error("Camera access error: ", err);
        resultDiv.textContent = "Error accessing camera. Please check permissions.";
    });

// Capture image from camera
captureButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    decodeQR(imageData);
});

// Decode QR from uploaded file
uploadButton.addEventListener('click', () => {
    const file = qrFileInput.files[0];
    if (!file) {
        resultDiv.textContent = "Please select a file.";
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        decodeQR(e.target.result);
    };
    reader.readAsDataURL(file);
});

// Function to display QR code data in an organized format
function displayData(data) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
    
        <table class="data-table">
           
            <tr><th>ID</th><td>${data.id}</td></tr>
            <tr><th>Name</th><td>${data.name}</td></tr>
            <tr><th>Email</th><td>${data.email}</td></tr>
            ${Object.entries(data.custom_fields || {})
                .map(([key, value]) => `<tr><th>${key}</th><td>${value}</td></tr>`)
                .join('')}
        </table>
    `;
}

// Function to send image data to the server for decoding
function decodeQR(imageData) {
    fetch('/decode_qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }
            return response.json();
        })
        .then((data) => {
            if (data.error) {
                document.getElementById('result').innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                displayData(data.data);
            }
        })
        .catch((err) => {
            console.error("Error decoding QR code: ", err);
            document.getElementById('result').innerHTML =
                '<p class="error">Error decoding QR code. Please try again.</p>';
        });
}
