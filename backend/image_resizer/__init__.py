import json, logging, zipfile, io
import azure.functions as func
from .utils import resize_image
from .config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY, AZURE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_STORAGE_KEY)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing multi-image upload...")

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

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file in req.files.getlist('image'):
                image_bytes = file.read()

                processed_image = resize_image(image_bytes, format=format_choice, add_watermark=add_watermark)

                new_filename = f"{file.filename.split('.')[0]}.{format_choice.lower()}"
                zip_file.writestr(new_filename, processed_image.getvalue())

        zip_buffer.seek(0)
        zip_name = "processed_images.zip"

        # Upload ZIP to Azure Blob Storage
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
