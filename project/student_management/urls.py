from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .views import (
    homepage, home, register, login_view, logout_view,
    events, booked_events, booked, cancel_booking,
    community, CommunityRequestCreateView,
    UpdateRequestViewSet, CommunityAdminViewSet, EventAdminViewSet,
    EventSearchViewSet, CommunitySearchViewSet, PostSearchViewSet,
    EventRequestCreateView, ProtectedEventsView, profile,
    send_test_email, search_posts,
    admin_community_requests, approve_community_request, reject_community_request,
    join_society, leave_society, join_community, societies_view,
    AdminSocietyRequestsView, CommentViewSet,
    add_comment, delete_comment,cancel_membership,
    friends_page, send_friend_request, accept_friend_request, reject_friend_request, remove_friend
)
from .views import CommentViewSet
from django.urls import path
from django.http import HttpResponse
from django.core.mail import send_mail

# REST Framework router
router = DefaultRouter()
router.register(r'update-requests', UpdateRequestViewSet, basename='update-request')
router.register(r'admin-communities', CommunityAdminViewSet, basename='community-admin')
router.register(r'admin-events', EventAdminViewSet, basename='event-admin')
router.register(r'search-events', EventSearchViewSet, basename='search-events')
router.register(r'search-communities', CommunitySearchViewSet, basename='search-communities')
router.register(r'search-posts', PostSearchViewSet, basename='search-posts')
router.register(r'comments', CommentViewSet, basename='comments')

def test_email(request):
    send_mail(
        '🚀 Test Email from Django (Docker)',
        'Hey Jana! This is a test email sent from your local Django app running in Docker. 🎉',
        'uweunihub@gmail.com',
        ['jana.tarek888@hotmail.com'],
        fail_silently=False,
    )
    return HttpResponse('Email sent successfully to jana.tarek888@hotmail.com')

urlpatterns = [
    # Public and Auth
    path('', homepage, name='homepage'),
    path('home/', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Events
    path('events/', events, name='events'),
    path('booked_events/', booked_events, name='booked_events'),
    path('booked/<int:event_id>/', booked, name='booked'),
    path('cancel_booking/<int:event_id>/', cancel_booking, name='cancel_booking'),
    path('request-event/', EventRequestCreateView.as_view(), name='request-event'),

    # Communities
    path('community/', community, name='community'),
    path('request-community/', CommunityRequestCreateView.as_view(), name='request-community'),
    path('join-community/<int:community_id>/', join_community, name='join_community'),
    path('cancel_community/<int:community_id>/', views.cancel_membership, name='cancel_community'),

    # Societies
    path('societies/', societies_view, name='societies'),
    path('societies/join/<int:society_id>/', join_society, name='join_society'),
    path('societies/leave/<int:society_id>/', leave_society, name='leave_society'),

    # Profile & Updates
    path('profile/', profile, name='profile'),
    path('update-request/', views.UpdateRequestCreateView.as_view(), name='update_request'),

    # Admin Approvals
    path('admin/community-requests/', admin_community_requests, name='admin_community_requests'),
    path('admin/community-requests/<int:request_id>/approve/', approve_community_request, name='approve_community'),
    path('admin/community-requests/<int:request_id>/reject/', reject_community_request, name='reject_community'),
    path('admin/update-requests/', views.approve_update_request, name='admin_update_requests'),
    path('admin/reject-update-request/<int:request_id>/', views.reject_update_request, name='reject_update_request'),
    path('admin_society_requests/', AdminSocietyRequestsView.as_view(), name='admin_society_requests'),
    path('admin_society_requests/<int:request_id>/', AdminSocietyRequestsView.as_view(), name='review_society_request'),

    # Friends System
    path('friends/', friends_page, name='friends'),
    path('friends/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<int:user_id>/', remove_friend, name='remove_friend'),

    # Search
    path('search-posts/', search_posts, name='search_posts'),

    # Comments
    path('add_comment/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    # API Auth
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/protected-events/', ProtectedEventsView.as_view(), name='protected_events'),

    # Test email
    path('send-test-email/', send_test_email, name='send_test_email'),

    path('send-test-email/', test_email),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
