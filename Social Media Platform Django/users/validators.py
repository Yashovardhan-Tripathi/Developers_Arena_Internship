from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def image_path(instance, filename):
    return f'images/{uuid4().hex}{Path(filename).suffix.lower()}'


def validate_image(upload):
    if Path(upload.name).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise ValidationError('Use a .jpg, .jpeg, .png, or .webp filename.')
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError('Images must be 5 MB or smaller.')
    try:
        upload.seek(0)
        with Image.open(upload) as img:
            expected = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}[Path(upload.name).suffix.lower()]
            if img.format != expected:
                raise ValidationError('The image format must match its filename.')
            if img.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValidationError('Use a JPEG, PNG, or WebP image.')
            if img.width * img.height > 20_000_000:
                raise ValidationError('Images must be smaller than 20 megapixels.')
            img.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, ValueError) as exc:
        raise ValidationError('Upload a valid image.') from exc
    finally:
        upload.seek(0)
