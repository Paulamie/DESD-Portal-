# Django Core
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy

# Auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Forms & Models
from .forms import UserRegisterForm, CommunityForm, UpdateRequestForm, EventForm, JoinSocietyForm
from .models import (
    Event, EventDetails, User, CommunityRequest, UpdateRequest,
    Community, Post, Society, CommunityMembership, Interest
)

# REST Framework
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

# Serializers
from .serializers import (
    UpdateRequestSerializer, CommunitySerializer, EventSerializer, PostSerializer
)

# Django Tools
from django.utils import timezone
from django.db.models import Q, Count
from django.views.generic import CreateView
from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import make_aware
from datetime import datetime
from itertools import chain
import random
from .models import SocietyJoinRequest 

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import SocietyJoinRequest
from .models import Notification
from django.contrib.auth import get_user_model


# Helper function to create notifications
def create_notification(user, message, notification_type='info'):
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
    )

# Home Views

def homepage(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'student_management/index.html')

@login_required
def home(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        if content:
            Post.objects.create(user=request.user, content=content)
            create_notification(request.user, f"Your post has been successfully created!", 'success')
            messages.success(request, "✅ Your post has been created successfully!")
            return redirect('home')


    posts = Post.objects.select_related('user').order_by('-timestamp')
    latest_update = UpdateRequest.objects.filter(user=request.user).order_by('-created_at').first()
    
    # NEW: Fetch friends, joined communities, and joined societies
    friends = User.objects.exclude(user_id=request.user.user_id)
    joined_communities = CommunityMembership.objects.filter(user=request.user).select_related('community')
    joined_societies = request.user.joined_societies.all()

    return render(request, 'student_management/home.html', {
        'posts': posts,
        'latest_update': latest_update,
        'friends': friends,
        'joined_communities': [membership.community for membership in joined_communities],
        'joined_societies': joined_societies,
    })


# Authentication Views

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'student_management/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'student_management/login.html', {'error': 'Invalid email or password'})
    return render(request, 'student_management/login.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')

def send_test_email(request):
    from django.core.mail import send_mail
    send_mail(
        subject='Test Email from Django',
        message='Hey! This is a test email to confirm your Django email is working.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['ilwadabdi234@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse(" Test email function works!!!!!")

# Event Views

@login_required
def events(request):
    query = request.GET.get('search', '')
    filter_option = request.GET.get('filter', '')
    society_filter = request.GET.get('society', '')
    community_filter = request.GET.get('community', '')

    approved_communities = Community.objects.filter(is_approved=True)
    community_requests = CommunityRequest.objects.filter(status='approved')
    events = Event.objects.filter(start_time__gte=timezone.now(), is_approved=True, community__in=approved_communities).order_by('-start_time')

    if query:
        events = events.filter(
            Q(event_name__icontains=query) |
            Q(info__icontains=query) |
            Q(actual_location__icontains=query)
        )

    if filter_option == 'online':
        events = events.filter(location_type='Online')
    elif filter_option == 'on-campus':
        events = events.filter(location_type='On-Campus')

    if society_filter:
        events = events.filter(society__society_id=society_filter)

    if community_filter:
        events = events.filter(community__community_id=community_filter)
        selected_community = Community.objects.filter(community_id=community_filter).first()
        if selected_community:
            community_requests = community_requests.filter(community_name=selected_community.community_name)

    booked_event_ids = EventDetails.objects.filter(user=request.user).values_list('event__event_id', flat=True)


    societies = Society.objects.all()
    communities = approved_communities

    return render(request, 'student_management/event.html', {
        'events': events,
        'community_requests': community_requests,
        'societies': societies,
        'communities': communities,
        'booked_event_ids': booked_event_ids,  # Send it to the template
    })

class EventRequestCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'student_management/event_form.html'
    success_url = reverse_lazy('events')

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)

@login_required
def booked_events(request):
    booked = EventDetails.objects.filter(user_id=request.user.user_id)
    return render(request, "student_management/booked_event.html", {'booked': booked})

@login_required
def booked(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    user = request.user

    if not EventDetails.objects.filter(event=event, user=user).exists():
        EventDetails.objects.create(event=event, user=user)
        create_notification(user, f"You booked the event '{event.event_name}'!", 'success')
        messages.success(request, f"✅ You have successfully booked '{event.event_name}'!")
    else:
        messages.info(request, f"ℹ️ You already booked '{event.event_name}'.")

    return redirect('events')


@login_required
def cancel_booking(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    user = request.user

    booking = EventDetails.objects.filter(event=event, user=user)
    if booking.exists():
        booking.delete()
        create_notification(user, f"You canceled booking for '{event.event_name}'.", 'info')
        messages.success(request, f"❌ You canceled your booking for '{event.event_name}'.")
    else:
        messages.error(request, "⚠️ You don't have a booking for this event.")

    return redirect('booked_events')


@login_required
def community(request):
    search_query = request.GET.get('search', '')
    filter_option = request.GET.get('filter', '')

    communities = Community.objects.filter(is_approved=True)
    community_requests = []

    if search_query:
        communities = communities.filter(
            Q(community_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if filter_option == 'my_requests' and request.user.is_authenticated:
        communities = communities.filter(com_leader=request.user)
        community_requests = CommunityRequest.objects.filter(requester=request.user)

        if search_query:
            community_requests = community_requests.filter(
                Q(community_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

    combined = list(chain(communities, community_requests))

    joined_ids = set()
    if request.user.is_authenticated:
        joined_ids = set(
            CommunityMembership.objects.filter(user=request.user)
            .values_list('community__community_id', flat=True)
        )

    return render(request, 'student_management/community.html', {
        'communities': combined,
        'joined_ids': joined_ids,
        'query': search_query,
        'filter_option': filter_option,
    })

class CommunityRequestCreateView(LoginRequiredMixin, CreateView):
    model = CommunityRequest
    form_class = CommunityForm
    template_name = 'student_management/community_form.html'
    success_url = reverse_lazy('community')

    def form_valid(self, form):
        form.instance.requester = self.request.user
        messages.success(self.request, "Your request has been submitted!")
        return super().form_valid(form)

@login_required
def profile(request):
    return render(request, 'student_management/profile.html', {'user': request.user})

@login_required
def join_society(request, society_id):
    society = get_object_or_404(Society, pk=society_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()

        # Check if a pending request already exists
        existing = SocietyJoinRequest.objects.filter(user=request.user, society=society)
        if existing.exists():
            messages.info(request, "You've already submitted a request for this society.")
            return redirect('societies')

        # Create the join request
        SocietyJoinRequest.objects.create(
            user=request.user,
            society=society,
            reason=reason,
            status='pending'
        )
        messages.success(request, f"✅ Your join request for {society.society_name} has been submitted.")
        return redirect('societies')

    return render(request, 'student_management/join_form.html', {
        'society': society
    })


@login_required
def leave_society(request, society_id):
    society = get_object_or_404(Society, pk=society_id)
    society.members.remove(request.user)
    messages.info(request, f"You've left {society.society_name}.")
    return redirect('societies')

@login_required
def join_community(request, community_id):
    community = get_object_or_404(Community, community_id=community_id, is_approved=True)
    already_member = CommunityMembership.objects.filter(user=request.user, community=community).exists()

    if not already_member:
        CommunityMembership.objects.create(user=request.user, community=community)
        messages.success(request, f"You joined {community.community_name} 🎉")
        
        # Create a notification for the user when they join a community
        create_notification(request.user, f"You successfully joined the community '{community.community_name}'!", 'success')

        
    else:
        messages.info(request, f"You're already a member of {community.community_name}")
    
    return redirect('community')


@login_required
def societies_view(request):
    user = request.user

    tag_filter = request.GET.get('tag')
    sort = request.GET.get('sort')

    all_tags = Interest.objects.all()
    joined_societies = user.joined_societies.all()
    new_societies = Society.objects.exclude(
        society_id__in=joined_societies.values_list('society_id', flat=True)
    )

    if tag_filter:
        new_societies = new_societies.filter(interests__name=tag_filter)

    if sort == 'popular':
        new_societies = new_societies.annotate(num_members=Count('members')).order_by('-num_members')
    elif sort == 'newest':
        new_societies = new_societies.order_by('-created_at')
    elif sort == 'alphabetical':
        new_societies = new_societies.order_by('society_name')

    user_tags = Interest.objects.filter(societies__in=joined_societies).distinct()
    recommended_societies = Society.objects.filter(
        interests__in=user_tags
    ).exclude(
        society_id__in=joined_societies.values_list('society_id', flat=True)
    ).distinct()[:5]

    for society in new_societies:
        society.mutual_friends = random.randint(0, 5)

    featured_society = Society.objects.annotate(num_members=Count('members')).order_by('-num_members').first()
    upcoming_events = Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')[:3]
    join_requests = SocietyJoinRequest.objects.filter(user=request.user)
    join_status_map = {req.society.society_id: req.status for req in join_requests}



    context = {
        'all_tags': all_tags,
        'joined_societies': joined_societies,
        'new_societies': new_societies,
        'featured_society': featured_society,
        'upcoming_events': upcoming_events,
        'recommended_societies': recommended_societies,
        'join_status_map': join_status_map,
    }

    return render(request, 'student_management/societies.html', context)

# Admin Views

@staff_member_required
def admin_community_requests(request):
    pending = CommunityRequest.objects.filter(status='pending')
    return render(request, 'student_management/admin_community_requests.html', {'requests': pending})

@staff_member_required
@require_POST
def approve_community_request(request, request_id):
    req = get_object_or_404(CommunityRequest, id=request_id)
    req.status = 'approved'
    req.reviewed_by = request.user
    req.save()


    create_notification(req.requester, f"Your community request for '{req.community_name}' has been approved!", 'success')

    return redirect('admin_community_requests')


@staff_member_required
@require_POST
def reject_community_request(request, request_id):
    req = get_object_or_404(CommunityRequest, id=request_id)
    req.status = 'rejected'
    req.reviewed_by = request.user
    req.save()
    create_notification(req.requester, f"Your community request for '{req.community_name}' has been rejected.", 'error')

    return redirect('admin_community_requests')

# REST API Views

class UpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = UpdateRequest.objects.all()
    serializer_class = UpdateRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UpdateRequest.objects.all()
        return UpdateRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommunityAdminViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        community = self.get_object()
        community.is_approved = True
        community.save()
        return Response({'status': 'approved'})
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        community = self.get_object()
        community.is_approved = False
        community.save()
        return Response({'status': 'rejected'})

class EventAdminViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        event = self.get_object()
        event.is_approved = True
        event.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        event = self.get_object()
        event.is_approved = False
        event.save()
        return Response({'status': 'rejected'})
class EventSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(is_approved=True).order_by('start_time')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['location_type', 'start_time']
    search_fields = ['event_name', 'info']

class CommunitySearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Community.objects.filter(is_approved=True)
    serializer_class = CommunitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['community_name', 'description']

class PostSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(visibility='public')
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'user__first_name', 'user__last_name', 'timestamp']

class ProtectedEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

@login_required
def search_posts(request):
    query = request.GET.get('search', '').strip()
    sort = request.GET.get('sort')
    posts = Post.objects.filter(visibility='public').select_related('user')

    if query:
        parsed_date = None
        today_year = datetime.now().year
        date_formats = ["%d/%m", "%d-%m", "%d/%m/%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(query, fmt)
                if "%Y" not in fmt:
                    parsed_date = parsed_date.replace(year=today_year)
                parsed_date = make_aware(parsed_date)
                break
            except ValueError:
                continue

        if parsed_date:
            posts = posts.filter(timestamp__date=parsed_date.date())
        else:
            posts = posts.filter(
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(timestamp__icontains=query) |
                Q(likes__icontains=query) |
                Q(comments_count__icontains=query)
            )

    if sort == 'oldest':
        posts = posts.order_by('timestamp')
    else:
        posts = posts.order_by('-timestamp')

    return render(request, 'student_management/search_posts.html', {
        'posts': posts,
        'query': query,
        'sort': sort
    })

class UpdateRequestCreateView(View):
    def get(self, request):
        form = UpdateRequestForm()
        return render(request, 'student_management/update_request.html', {'form': form})

    def post(self, request):
        form = UpdateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            field = form.cleaned_data['field_to_update']
            new_value = form.cleaned_data['new_value']
            profile_picture = request.FILES.get('profile_picture')

            if field == 'name':
                old = request.user.get_full_name()
            elif field == 'course':
                old = request.user.course
            else:
                old = ''

            UpdateRequest.objects.create(
                user=request.user,
                field_to_update=field.capitalize(),
                old_value=old,
                new_value=new_value if field != 'profile_picture' else '',
                profile_picture=profile_picture if field == 'profile_picture' else None,
                status='pending',
                created_at=timezone.now()
            )

            messages.success(request, "Your update request was submitted.")
            return redirect('home')

        return render(request, 'student_management/update_request.html', {'form': form})
    
@staff_member_required
@require_POST
def approve_update_request(request, request_id):
    update_request = get_object_or_404(UpdateRequest, id=request_id)
    update_request.status = 'approved'
    update_request.save()

    # Apply the changes to the user profile
    user = update_request.user
    if update_request.field_to_update == 'name':
        user.first_name, user.last_name = update_request.new_value.split(' ', 1)
    elif update_request.field_to_update == 'course':
        user.course = update_request.new_value
    elif update_request.field_to_update == 'profile_picture':
        user.profile_picture = update_request.profile_picture

    user.save()


    create_notification(user, f"Your update request for '{update_request.field_to_update}' has been approved!", 'success')

    messages.success(request, f"{user.username}'s update request has been approved.")
    return redirect('admin_update_requests')


@staff_member_required
@require_POST
def reject_update_request(request, request_id):
    update_request = get_object_or_404(UpdateRequest, id=request_id)
    update_request.status = 'rejected'
    update_request.save()


    create_notification(update_request.user, f"Your update request for '{update_request.field_to_update}' has been rejected.", 'error')

    messages.warning(request, f"{update_request.user.username}'s update request has been rejected.")
    return redirect('admin_update_requests')





User = get_user_model()

def friends(request):
    friends = User.objects.exclude(user_id=request.user.user_id)
    return render(request, 'student_management/friends.html', {'friends': friends})


@method_decorator(staff_member_required, name='dispatch')
class AdminSocietyRequestsView(View):
    def get(self, request):
        join_requests = SocietyJoinRequest.objects.all().order_by('-created_at')
        return render(request, 'admin_society_requests.html', {'join_requests': join_requests})

    def post(self, request, request_id):
        join_request = get_object_or_404(SocietyJoinRequest, id=request_id)
        action = request.POST.get('action')

        if action == 'approve':
            join_request.status = 'approved'
            join_request.save()
            # Creating a notification for the user when their join request is approved

            create_notification(join_request.user, f"Your join request to '{join_request.society.society_name}' has been approved!", 'success')

            messages.success(request, f"{join_request.user.username}'s join request to {join_request.society.society_name} has been approved.")

        elif action == 'reject':
            join_request.status = 'rejected'
            join_request.save()
            # Creating a notification for the user when their join request is rejected

            create_notification(join_request.user, f"Your join request to '{join_request.society.society_name}' has been rejected!", 'error')


            messages.warning(request, f"{join_request.user.username}'s join request to {join_request.society.society_name} has been rejected.")

        return redirect('admin_society_requests')
    
@staff_member_required
def admin_update_requests(request):
    updates = UpdateRequest.objects.all().order_by('-created_at')
    return render(request, 'student_management/admin_update_requests.html', {'updates': updates})
