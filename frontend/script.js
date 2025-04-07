const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusText = document.getElementById('status');
const downloadLink = document.getElementById('download-link');
const resultContainer = document.getElementById('result');
const formatSelect = document.getElementById('format');
const watermarkCheckbox = document.getElementById('watermark');

// Your backend function URL (change this when deploying to Azure)
const API_URL = "https://serverless-resizer.azurewebsites.net/api/image_resizer"; // Local Testing
// const API_URL = "https://your-azure-function-url/api/image_resizer"; // Uncomment when deployed

let selectedFiles = null;

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

    selectedFiles = e.dataTransfer.files;
    if (selectedFiles.length > 0) {
        statusText.textContent = `${selectedFiles.length} file(s) selected via drop`;
    }
});

// File Input Click
dropArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0){
        statusText.textContent = `${files.length} file(s) selected`;
    }
});

// Upload Image to Backend
uploadBtn.addEventListener('click', async () => {
    const files = selectedFiles || fileInput.files;
    if (!files || !files.length) {
        statusText.textContent = "Please select at least one file first!";
        return;
    }

    const format = formatSelect.value;
    const watermark = watermarkCheckbox.checked ? "true" : "false";

    const formData = new FormData();
    for (const file of files){
        formData.append("image", file);
    }
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
        if(data.zip_url){
            downloadLink.href = data.zip_url;
            downloadLink.textContent = "Download Processed Images";
        }
        else if (data.processed_image_url){
            downloadLink.href = data.processed_image_url;
            downloadLink.textContent = "Download Processed Images";
        }
        resultContainer.style.display = "block";
        statusText.textContent = "Upload successful!";
    } catch (error) {
        console.error("Error:", error.message);
        statusText.textContent = "Error: " + error.message;
    }
});
