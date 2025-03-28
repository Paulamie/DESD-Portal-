from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User
from .models import CommunityRequest, Interest


# from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class CommunityForm(forms.ModelForm):
    class Meta:
        model = CommunityRequest
        fields = ['community_name', 'description', 'purpose', 'interests']
        widgets = {
            'interests': forms.SelectMultiple(attrs={
                'style': 'width:100%; height:120px; padding:8px;',
                'class': 'form-control',
            }),
        }

from .models import UpdateRequest  # Add this import at the top of your forms.py


from django import forms
from .models import UpdateRequest

from django import forms
from .models import UpdateRequest

class UpdateRequestForm(forms.ModelForm):
    FIELD_CHOICES = [
        ('name', 'Name'),
        ('course', 'Course'),
        ('profile_picture', 'Profile Picture'),
    ]

    field_to_update = forms.ChoiceField(choices=FIELD_CHOICES)
    old_value = forms.CharField(required=False)
    new_value = forms.CharField(required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = UpdateRequest
        fields = ['field_to_update', 'old_value', 'new_value', 'profile_picture']
