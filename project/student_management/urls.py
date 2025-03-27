from django.urls import path
from .views import homepage, home, register, login_view, logout_view ,events,booked_events,booked,cancel_booking,communityform,community
#profile



urlpatterns = [
    path('', homepage, name='homepage'),  # Shows login/signup buttons
    path('home/', home, name='home'),  # Redirect after login/signup
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('events/',events,name='events'),
    path('logout/', logout_view, name='logout'),
    path('booked_events/', booked_events ,name='booked_events'),
    path('booked/<int:event_id>/', booked, name='booked'),
    path('cancel_booking/<int:event_id>/', cancel_booking, name='cancel_booking'),
    path('request-community/', communityform, name='request-community'),
    path('community',community,name='community')
    # path('profile/', profile, name='profile'),
    # path('', Home.as_view()),
]
