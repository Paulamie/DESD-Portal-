from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User, CommunityRequest, Interest, Event, UpdateRequest
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


# === User Registration Form ===
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


# === Community Request Form ===
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['interests'].queryset = Interest.objects.all()


# === Update Request Form ===
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


# === Event Form with Validations ===
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'start_time', 'end_time', 'info', 'community', 'society', 'location_type', 'actual_location','maximum_capacity']

    current_time = timezone.now()

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'step': 60}),
        validators=[MinValueValidator(current_time, message="Start Datetime cannot be in the past.")],
        initial=current_time.replace(second=0, microsecond=0)
    )

    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'step': 60}),  # step 60 = no seconds
        validators=[MinValueValidator(current_time, message="End Datetime cannot be in the past.")],
        initial=current_time.replace(second=0, microsecond=0)
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise ValidationError("End Datetime must be after Start Datetime.")
        return cleaned_data


class JoinSocietyForm(forms.Form):
    reason = forms.CharField(
        label="Why do you want to join this society?",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=True
    )

