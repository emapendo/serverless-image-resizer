# 📸 Serverless Image Resizer
A **serverless image processing tool** that allows users to **upload, resize, compress, and convert images effortlessly**. Built using **Azure Functions** for the backend and a lightweight **HTML, CSS, and JavaScript frontend**.

---

## 🚀 Features
✅ **Drag & Drop Image Upload** – Users can select or drop images for processing.  
✅ **Resize & Compress Images** – Optimizes file size while maintaining quality.  
✅ **Convert Formats** – Supports **JPG, PNG, WEBP** output.  
✅ **Watermarking** – Optionally adds a **"CS496"** watermark.  
✅ **Cloud Storage** – Processed images are stored on **Azure Blob Storage**.  
✅ **Serverless Architecture** – Hosted on **Azure Functions** for scalability.  

---

## 📂 Project Structure
```sh
serverless-image-resizer/
│── backend/
│   │── image_resizer/
│   │   │── __init__.py       # Azure Function logic
│   │   │── function.json     # Function trigger configuration
│   │   │── utils.py          # Image processing logic
│   │   │── config.py         # Configuration file (excluded from Git)
│   ├── local.settings.json   # Local environment settings (excluded from Git)
│   ├── requirements.txt      # Python dependencies
│── frontend/
│   │── index.html            # Web UI
│   │── styles.css            # UI styles
│   │── script.js             # Handles user interactions and API calls
│── .gitignore                # Ignores sensitive & unnecessary files
│── README.md                 # Project documentation
```
---

## 💻 Setup & Installation

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/emapendo/serverless-image-resizer.git
cd serverless-image-resizer

cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

📌 Set Up Environment Variables
Create a .env file in backend/image_resizer:

AZURE_STORAGE_ACCOUNT=your-storage-account
AZURE_STORAGE_KEY=your-secret-key
AZURE_CONTAINER_NAME=processed-images
MAX_WIDTH=800
MAX_HEIGHT=600
```
