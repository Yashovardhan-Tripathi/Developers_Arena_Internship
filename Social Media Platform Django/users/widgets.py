from django.forms import ClearableFileInput


class PrivateImageInput(ClearableFileInput):
    # Existing files remain clearable without exposing raw storage paths.
    template_name = 'partials/private_image_input.html'
