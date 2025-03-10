from django.urls import path
from .views import homepage, home, register, login_view, logout_view ,events

urlpatterns = [
    path('', homepage, name='homepage'),  # Shows login/signup buttons
    path('home/', home, name='home'),  # Redirect after login/signup
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('events/',events,name='events'),
    path('logout/', logout_view, name='logout'),
]
