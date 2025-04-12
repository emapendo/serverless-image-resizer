import json, logging, zipfile, io
import azure.functions as func
from .utils import resize_image
from .config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY, AZURE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timezone

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_STORAGE_KEY)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing image upload...")

    try:
        if not req.files:
            return func.HttpResponse(
                json.dumps({"error": "No image uploaded"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        format_choice = req.form.get("format", "JPEG").upper()
        add_watermark = req.form.get("watermark", "false").lower() == "true"

        uploaded_files = req.files.getlist("image")

        if len(uploaded_files) == 1:
            # ✅ Single image mode
            file = uploaded_files[0]
            image_bytes = file.read()

            processed_image = resize_image(image_bytes, format=format_choice, add_watermark=add_watermark)
            new_filename = f"{file.filename.split('.')[0]}.{format_choice.lower()}"

            blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=new_filename)
            blob_client.upload_blob(processed_image.getvalue(), overwrite=True)

            image_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{new_filename}"

            return func.HttpResponse(
                json.dumps({"processed_image_url": image_url}),
                status_code=200,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        else:
            # ✅ Multiple image mode – ZIP bundle
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file in uploaded_files:
                    image_bytes = file.read()
                    processed_image = resize_image(image_bytes, format=format_choice, add_watermark=add_watermark)
                    new_filename = f"{file.filename.split('.')[0]}.{format_choice.lower()}"
                    zip_file.writestr(new_filename, processed_image.getvalue())

            zip_buffer.seek(0)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            zip_name = f"processed_{timestamp}.zip" # processed_20250411_1429.zip
            blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=zip_name)
            blob_client.upload_blob(zip_buffer.getvalue(), overwrite=True)

            zip_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{zip_name}"

            return func.HttpResponse(
                json.dumps({"zip_url": zip_url}),
                status_code=200,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
