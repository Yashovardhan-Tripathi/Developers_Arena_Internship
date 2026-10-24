from django import forms
from users.forms import StyledForm
from .models import Post
from users.widgets import PrivateImageInput


class PostForm(StyledForm, forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'visibility']
        widgets = {'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share something worth connecting over...', 'aria-label': 'Post content'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style()
        self.fields['image'].widget = PrivateImageInput(attrs={'class': 'form-control'})
        self.fields['image'].widget.attrs['accept'] = 'image/jpeg,image/png,image/webp'

    def clean(self):
        data = super().clean()
        if not data.get('content', '').strip() and not data.get('image'):
            raise forms.ValidationError('Write something or add an image.')
        return data
