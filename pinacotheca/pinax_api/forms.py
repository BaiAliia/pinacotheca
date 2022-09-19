from django import forms
import sys
sys.path.append("./")

from pinax.models import ImageModel

class ImageForm(forms.ModelForm):
    class Meta:
       model = ImageModel
       fields = ('image', 'painting')
