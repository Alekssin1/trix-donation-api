import os
from PIL import Image
from io import BytesIO
from users.tasks import remove_old_image
from django.core.files.uploadedfile import InMemoryUploadedFile


def convert_image_to_webp(image_field):
    from django.conf import settings

    old_path = os.path.join(settings.MEDIA_ROOT, str(image_field))
    if image_field and not image_field.name.lower().endswith('.webp'):
        img = Image.open(image_field)
        buffer = BytesIO()
        img.save(buffer, format='WEBP')
        buffer.seek(0)
        # remove_old_image(old_path)
        remove_old_image.s(old_path).apply_async(countdown=10)
        return InMemoryUploadedFile(buffer, 'ImageField', f"{image_field.name.split('.')[0]}.webp", 'image/webp', buffer.getbuffer().nbytes, None)
    # remove_old_image(old_path)
    remove_old_image.s(old_path).apply_async(countdown=10)
    return image_field