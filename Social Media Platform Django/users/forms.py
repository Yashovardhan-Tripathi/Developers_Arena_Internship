from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import UserProfile
from .widgets import PrivateImageInput


class StyledForm:
    def style(self):
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'


class SignupForm(StyledForm, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style()


class ProfileForm(StyledForm, forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'bio', 'profile_picture', 'cover_photo', 'location', 'website', 'is_private', 'default_visibility']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget = PrivateImageInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'})
        self.fields['cover_photo'].widget = PrivateImageInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'})
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.style()

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save(update_fields=['first_name', 'last_name'])
            profile.save()
        return profile
