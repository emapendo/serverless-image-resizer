const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusText = document.getElementById('status');
const outputImg = document.getElementById('output-img');
const resultContainer = document.getElementById('result');
const formatSelect = document.getElementById('format');
const watermarkCheckbox = document.getElementById('watermark');

// Your backend function URL (change this when deploying to Azure)
const API_URL = "https://serverless-resizer.azurewebsites.net/api/image_resizer"; // Local Testing
// const API_URL = "https://your-azure-function-url/api/image_resizer"; // Uncomment when deployed

let selectedFile = null;

// Drag & Drop File Handling
dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.style.background = "#e3e3e3";
});

dropArea.addEventListener('dragleave', () => {
    dropArea.style.background = "#fafafa";
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.style.background = "#fafafa";

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        selectedFile = files[0];
        statusText.textContent = `Selected: ${selectedFile.name}`;
    }
});

// File Input Click
dropArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];
    statusText.textContent = `Selected: ${selectedFile.name}`;
});

// Upload Image to Backend
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        statusText.textContent = "Please select a file first!";
        return;
    }

    const format = formatSelect.value;
    const watermark = watermarkCheckbox.checked ? "true" : "false";

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("format", format);
    formData.append("watermark", watermark);

    statusText.textContent = "Uploading...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            mode: "cors",
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Upload failed");
        }

        console.log("Response:", data);
        outputImg.src = data.processed_image_url;
        resultContainer.style.display = "block";
        statusText.textContent = "Upload successful!";
    } catch (error) {
        console.error("Error:", error.message);
        statusText.textContent = "Error: " + error.message;
    }
});