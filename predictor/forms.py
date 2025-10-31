from django import forms

class UploadForm(forms.Form):
    audio_file = forms.FileField(required=False)
    image_file = forms.ImageField(required=False)
    use_audio = forms.BooleanField(required=False, initial=True)
    use_image = forms.BooleanField(required=False, initial=False)
