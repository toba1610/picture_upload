from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ALLOWED_EXTENSIONS = {'.heic', '.heif', '.jpeg', '.jpg', '.png', '.webp'}


def create_picture_filename(original_filename: str) -> str:

	'''
		Creates a unique filename for the uploaded picture based on the current UTC timestamp and a random UUID.
	'''

	extension = Path(original_filename).suffix.lower()
	if extension not in ALLOWED_EXTENSIONS:
		raise ValueError('Bitte ein JPG-, PNG-, WEBP- oder HEIC-Bild verwenden.')

	timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
	return f'{timestamp}_{uuid4().hex[:8]}{extension}'
