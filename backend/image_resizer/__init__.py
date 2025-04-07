import json, logging, uuid, io, zipfile
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from .utils import resize_image
from .config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY, AZURE_CONTAINER_NAME

# Initialize Azure Blob Storage Client
blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_STORAGE_KEY)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing image upload...")

    try:
        # Get the uploaded file
        file = req.files.get('image')
        if not file:
            return func.HttpResponse(
                json.dumps({"error": "No image uploaded"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}  # ✅ Force CORS Header
            )

        # Get user preferences (format and watermark)
        format_choice = req.form.get("format", "JPEG").upper()  # Default to JPEG
        add_watermark = req.form.get("watermark", "false").lower() == "true"  # Default to False

        # Read file bytes
        image_bytes = file.read()

        # Resize, convert format, and apply watermark if requested
        processed_image = resize_image(image_bytes, format=format_choice, add_watermark=add_watermark)

        # Upload to Azure Blob Storage
        new_filename = f"{file.filename.split('.')[0]}.{format_choice.lower()}"
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=new_filename)
        blob_client.upload_blob(processed_image.getvalue(), overwrite=True)

        # Generate processed image URL
        processed_image_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{new_filename}"

        logging.info(f"Processed image URL: {processed_image_url}")

        return func.HttpResponse(
            json.dumps({"processed_image_url": processed_image_url}),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}  # ✅ Force CORS Header
        )

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}  # ✅ Force CORS Header
        )
