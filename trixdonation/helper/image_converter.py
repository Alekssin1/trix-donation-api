from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def convert_image_to_webp(image_field):
    if image_field and not image_field.name.lower().endswith('.webp'):
        img = Image.open(image_field)
        buffer = BytesIO()
        img.save(buffer, format='WEBP')
        buffer.seek(0)
        return InMemoryUploadedFile(buffer, 'ImageField', f"{image_field.name.split('.')[0]}.webp", 'image/webp', buffer.getbuffer().nbytes, None)
    return image_field