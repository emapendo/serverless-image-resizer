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
    logging.info("Processing multi-image upload...")

    try:
        # Get the uploaded file
        files = req.files.get('image')
        if not files:
            return func.HttpResponse(
                json.dumps({"error": "No image uploaded"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}  # ✅ Force CORS Header
            )
        # If only one file is uploaded then wrap it in a list
        if not isinstance(files, list):
            files = [files]

        # Get user preferences (format and watermark)
        format_choice = req.form.get("format", "JPEG").upper()  # Default to JPEG
        add_watermark = req.form.get("watermark", "false").lower() == "true"  # Default to False

        processed_images = []
        errors = []

        for file in files:
            try:
                # Read file bytes
                image_bytes = file.read()
        
                # Resize, convert format, and apply watermark if requested
                processed_image = resize_image(image_bytes, format=format_choice, add_watermark=add_watermark)

                # Create a new filename for the processed image
                new_filename = f"{file.filename.split('.')[0]}.{format_choice.lower()}"
                processed_images.append((new_filename, processed_image.getvalue()))
            except Exception as e:
                logging.error(f"Error processing {file.filename}: {e}")
                errors.append({"file": file.filename, "error": str(e)})
        if not processed_images:
            return func.HttpResponse(
                json.dumps({"error": "None of the images were able to be processed."}),
                status_code = 400,
                mimetype = "application/json",
                headers = {"Access-Control-Allow-Origin": "*"}  # ✅ Force CORS Header
            )

        # Create a ZIP archive in memory to contain all the processed images
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, image_data in processed_images:
                zipf.writestr(filename, image_data)
        zip_buffer.seek(0)
        
        # Upload the ZIP Azure Blob Storage
        zip_filename = f"batch_{uuid.uuid4().hex}.zip"
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=zip_filename)
        blob_client.upload_blob(zip_buffer.getvalue(), overwrite=True)

        # Generate processed image URL
        zip_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{zip_filename}"

        # Prepare response
        response_data = {"zip_url": zip_url}
        if errors:                                        # Includes individual errors
            response_data["errors"] = errors

        return func.HttpResponse(
            json.dumps(response_data),
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
