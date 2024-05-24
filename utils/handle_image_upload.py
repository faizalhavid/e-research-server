from PIL import Image

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
        img = Image.open(instance.image.path)

        width, height = img.size
        if width != height:
            new_size = min(width, height)
            left = (width - new_size)/2
            top = (height - new_size)/2
            right = (width + new_size)/2
            bottom = (height + new_size)/2

            img = img.crop((left, top, right, bottom))
            img.save(instance.image.path)