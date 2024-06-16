from PIL import Image
from django.core.files.storage import default_storage
from io import BytesIO

def handle_image_replacement(instance):
    if instance.image:
        try:
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            if old_instance.image != instance.image:
                old_instance.image.delete(save=False)
        except instance.__class__.DoesNotExist:
            pass


def crop_image_to_square(instance):
    if instance.image:
        # Open the image using Django's storage backend
        with default_storage.open(instance.image.name, 'rb') as image_file:
            img = Image.open(image_file)

            width, height = img.size
            if width != height:
                new_size = min(width, height)
                left = (width - new_size) / 2
                top = (height - new_size) / 2
                right = (width + new_size) / 2
                bottom = (height + new_size) / 2

                img = img.crop((left, top, right, bottom))

                # Save the cropped image back to storage
                with BytesIO() as buffer:
                    img.save(buffer, format=img.format)
                    buffer.seek(0)
                    instance.image.save(instance.image.name, buffer, save=False)