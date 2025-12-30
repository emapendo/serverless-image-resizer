import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Storage details
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# Max Image Dimensions
MAX_WIDTH = int(os.getenv("MAX_WIDTH", 800))
MAX_HEIGHT = int(os.getenv("MAX_HEIGHT", 600))
FUNCTION_KEY = os.getenv("FUNCTION_KEY")
