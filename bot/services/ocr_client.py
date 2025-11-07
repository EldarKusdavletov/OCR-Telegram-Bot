import logging
import requests

from config import UPSTAGE_API_KEY, OCR_API_URL


def process_image_with_ocr(image_bytes: bytes) -> dict:
    """
    Sends an image to the Upstage OCR API and returns the result.
    Raises an exception on API error.
    """
    try:
        headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
        files = {"document": ("image.jpg", image_bytes, "image/jpeg")}
        data = {"model": "ocr"}

        response = requests.post(OCR_API_URL, headers=headers, files=files, data=data)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - {response.text}")
        raise Exception(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"An error occurred in OCR client: {e}")
        raise e
