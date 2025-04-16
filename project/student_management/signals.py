from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

#you can change the function whatever
@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created and not instance.is_verified:  
        subject = 'Please confirm your email address'
        message = f'Thank you for registering. Please click the link below to confirm your email address:\n\n{settings.SITE_URL}/verify/{instance.pk}/'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False,
        )
        
#function to send email when a community request is approved or rejected
#function to send email when user books an event
#function to send email when user cancels booking for an event
