const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusText = document.getElementById('status');
const outputImg = document.getElementById('output-img');
const resultContainer = document.getElementById('result');
const formatSelect = document.getElementById('format');
const watermarkCheckbox = document.getElementById('watermark');
const previewContainer = document.getElementById('preview-container');

const API_URL = "https://serverless-resizer.azurewebsites.net/api/image_resizer";

let selectedFiles = [];

// Handle drag & drop
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
    handleFiles(e.dataTransfer.files);
});

// Clicking drop area opens file selector
dropArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

// Helper: render preview
function renderPreview() {
    previewContainer.innerHTML = "";
    selectedFiles.forEach((file, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.classList.add('preview-item');

        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        img.classList.add('preview-thumb');

        const removeBtn = document.createElement('button');
        removeBtn.textContent = "x";
        removeBtn.classList.add('remove-btn');
        removeBtn.onclick = () => {
            selectedFiles.splice(index, 1);
            renderPreview();
        };

        fileDiv.appendChild(img);
        fileDiv.appendChild(removeBtn);
        previewContainer.appendChild(fileDiv);
    });

    statusText.textContent = selectedFiles.length
        ? `${selectedFiles.length} image(s) selected`
        : "No images selected";
}

// Handle adding new files
function handleFiles(files) {
    for (let file of files) {
        if (file.type.startsWith('image/')) {
            selectedFiles.push(file);
        }
    }
    renderPreview();
}

// Upload files
uploadBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        statusText.textContent = "Please select at least one image.";
        return;
    }

    const format = formatSelect.value;
    const watermark = watermarkCheckbox.checked ? "true" : "false";

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append("image", file); // same key for multiple files
    });
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
        if (!response.ok) throw new Error(data.error || "Upload failed");

        resultContainer.innerHTML = `
            <h3>Download ZIP:</h3>
            <a href="${data.zip_url}" target="_blank" download>Click here to download processed images</a>
        `;
        resultContainer.style.display = "block";
        statusText.textContent = `Upload successful!`;
    } catch (err) {
        console.error(err);
        statusText.textContent = `Error uploading: ${err.message}`;
    }

    selectedFiles = [];
    renderPreview();
});
