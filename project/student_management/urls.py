from django.urls import path, include
from . import views
from .views import profile 
from .views import (
    homepage, home, register, login_view, logout_view,
    events, booked_events, booked, cancel_booking,
    community, CommunityRequestCreateView,
    PostSearchViewSet, EventAdminViewSet,
    UpdateRequestViewSet, CommunityAdminViewSet,
    EventSearchViewSet, CommunitySearchViewSet,
    admin_community_requests, approve_community_request, reject_community_request,send_test_email
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProtectedEventsView
from .views import search_posts


# REST Framework ViewSets
router = DefaultRouter()
router.register(r'update-requests', UpdateRequestViewSet, basename='update-request')
router.register(r'admin-communities', CommunityAdminViewSet, basename='community-admin')
router.register(r'admin-events', EventAdminViewSet, basename='event-admin')
router.register(r'search-events', EventSearchViewSet, basename='search-events')
router.register(r'search-communities', CommunitySearchViewSet, basename='search-communities')
router.register(r'search-posts', PostSearchViewSet, basename='search-posts')

urlpatterns = [
    path('', homepage, name='homepage'),
    path('home/', views.home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('events/', events, name='events'),
    path('booked_events/', booked_events, name='booked_events'),
    path('booked/<int:event_id>/', booked, name='booked'),
    path('cancel_booking/<int:event_id>/', cancel_booking, name='cancel_booking'),
    path('request-community/', CommunityRequestCreateView.as_view(), name='request-community'),
    path('community/', community, name='community'),
    path('update-request/', views.UpdateRequestCreateView.as_view(), name='update_request'),
    path('profile/', profile, name='profile'),
    path('societies/', views.societies, name='societies'),
    path('test-email/', views.send_test_email, name='test-email'), 



    # Admin Panel Views for Approving/Rejecting Community Requests
    path('admin/community-requests/', admin_community_requests, name='admin_community_requests'),
    path('admin/community-requests/<int:request_id>/approve/', approve_community_request, name='approve_community'),
    path('admin/community-requests/<int:request_id>/reject/', reject_community_request, name='reject_community'),
    

    # REST API paths
    path('api/', include(router.urls)),

    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/protected-events/', ProtectedEventsView.as_view(), name='protected_events'),
    path('search-posts/', search_posts, name='search_posts'),
]
