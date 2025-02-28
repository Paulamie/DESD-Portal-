from django.urls import path
from .views import register, login_view
from .views import home

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    
]

