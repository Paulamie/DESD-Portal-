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
        # form fields
        fields = ['community_name', 'description', 'purpose', 'interests']
        widgets = {
            # make the interest come up as a dropdown so user can choose
            'interests': forms.SelectMultiple(),
        }
# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']
    
# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['course', 'bio', 'profile_picture']