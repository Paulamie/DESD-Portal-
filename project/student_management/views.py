# Django Core
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy

# Auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Forms & Models
from .forms import UserRegisterForm, CommunityForm
from .models import Event, EventDetails, User, CommunityRequest, Post

# REST Framework
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# ViewSets
from .serializers import UpdateRequestSerializer, CommunitySerializer, EventSerializer

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from django.views.generic.edit import CreateView

from .models import UpdateRequest


from .models import Community

from .models import Event, EventDetails, User, CommunityRequest, UpdateRequest, Community, Post

from .serializers import PostSerializer 

from django.utils import timezone
from django.views import View
from django.shortcuts import render, redirect
from .models import UpdateRequest
from .forms import UpdateRequestForm

from django.views import View
from django.utils import timezone
from django.db.models import Q







def homepage(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect logged-in users to home
    return render(request, 'student_management/index.html')

@login_required
def home(request):
    if request.method == 'POST':
        content = request.POST.get('post_content')
        if content:
            Post.objects.create(user=request.user, content=content)
            return redirect('homepage')

    posts = Post.objects.select_related('user').order_by('-timestamp')
    context = {'posts': posts}
    
    return render(request, 'student_management/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home after registration
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
            return redirect('home')  # Redirect to home after login
        else:
            return render(request, 'student_management/login.html', {'error': 'Invalid email or password'})
    return render(request, 'student_management/login.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')

def events(request):
    query = request.GET.get('search', '')
    filter_option = request.GET.get('filter', '')

    events = Event.objects.all()

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

    return render(request, 'student_management/event.html', {'events': events})


# class EventListView(ListView):
#     model = Event
#     context_object_name = 'events'  
#     template_name = 'student_management/event.html'  



from django.db.models import Q

from django.db.models import Q

from django.db.models import Q

def community(request):
    search_query = request.GET.get('search', '')
    filter_option = request.GET.get('filter', '')

    communities = Community.objects.filter(is_approved=True)

    if search_query:
        communities = communities.filter(
            Q(community_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if filter_option == 'my_requests':
        communities = communities.filter(com_leader=f"{request.user.first_name} {request.user.last_name}")

    return render(request, 'student_management/community.html', {
        'communities': communities
    })





def booked_events(request):
    user = request.user  #get the current user 
    #filters the event details based on user_id logged in 
    booked = EventDetails.objects.filter(user_id=request.user.user_id)
    return render(request, "student_management/booked_event.html", {'booked': booked})

def booked(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)  
    
    print(f"User Object: {request.user}")  # Debugging line
    print(f"User PK: {request.user.pk}")  # Debugging line

    # Ensure the user exists in the database
    user = get_object_or_404(User, user_id=request.user.pk)

    # Check if the user has already booked this event
    existing_booking = EventDetails.objects.filter(event=event, user=user).exists()

    #if it doesnt exist would add it to the database
    if not existing_booking:
        EventDetails.objects.create(event=event, user=user)

    # redirect to the my booked events page
    return redirect('booked_events')  


def cancel_booking(request, event_id):
    #get the event and user models event_id and their user_id 
    event = get_object_or_404(Event, event_id=event_id)
    user = get_object_or_404(User, user_id=request.user.pk)

    #filter both the event_id and user_id
    booking = EventDetails.objects.filter(event=event, user=user)
    
    #if found 
    if booking.exists():
        #delete the booking and display message
        booking.delete()
        messages.success(request, "Your booking has been canceled successfully.")
    else:
        #else display this
        messages.error(request, "You don't have a booking for this event.")

    #redirect to my_booked events page
    return redirect('booked_events') 



class CommunityRequestCreateView(LoginRequiredMixin, CreateView):
    #use the model and form
    model = CommunityRequest
    form_class = CommunityForm
    template_name = 'student_management/community_form.html'
    #if sucessful redirect to the community page
    success_url = reverse_lazy('community')  

    def form_valid(self, form):
        #get the user_id of the requester that is logged in 
        form.instance.requester = self.request.user
        #save the form
        response = super().form_valid(form)
        #display the message
        messages.success(self.request, "Your request has been submitted!")
        return response
    
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
    serializer_class = EventSerializer  # Use your existing serializer
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
    search_fields = ['content']

from .models import CommunityRequest

from django.contrib.admin.views.decorators import staff_member_required  # only admin users
from django.shortcuts import render, redirect

@staff_member_required
def admin_community_requests(request):
    requests = CommunityRequest.objects.filter(status='pending')
    return render(request, 'student_management/admin_community_requests.html', {'requests': requests})

@staff_member_required
def approve_community_request(request, request_id):
    req = CommunityRequest.objects.get(pk=request_id)
    req.status = 'approved'
    req.save()
    return redirect('admin_community_requests')

@staff_member_required
def reject_community_request(request, request_id):
    req = CommunityRequest.objects.get(pk=request_id)
    req.status = 'rejected'
    req.save()
    return redirect('admin_community_requests')



from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

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

    # Optional: auto-create Community
    Community.objects.create(
        com_leader=req.requester.get_full_name(),
        community_name=req.community_name,
        description=req.description,
        is_approved=True
    )
    return redirect('admin_community_requests')

@staff_member_required
@require_POST
def reject_community_request(request, request_id):
    req = get_object_or_404(CommunityRequest, id=request_id)
    req.status = 'rejected'
    req.reviewed_by = request.user
    req.save()
    return redirect('admin_community_requests')

from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .forms import UpdateRequestForm
from .models import UpdateRequest

class UpdateRequestCreateView(CreateView):
    model = UpdateRequest
    form_class = UpdateRequestForm
    template_name = 'student_management/update_request.html'
    success_url = '/profile'  # or redirect to any page after submission

    def form_valid(self, form):
        # Ensure the user submitting the form is logged in
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateRequestCreateView(View):
    def get(self, request):
        form = UpdateRequestForm()
        return render(request, 'student_management/update_request.html', {'form': form})

    def post(self, request):
        form = UpdateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            field = form.cleaned_data['field_to_update']
            old = form.cleaned_data['old_value']
            new = form.cleaned_data['new_value']
            pic = request.FILES.get('profile_picture')

            update_request = UpdateRequest.objects.create(
                user=request.user,
                field_to_update=field,
                old_value=old,
                new_value=new if field != 'Profile Picture' else (pic.name if pic else ''),
                status='pending',
                created_at=timezone.now()
            )

            return redirect('home')

        print("FORM ERRORS:", form.errors)

        return render(request, 'student_management/update_request.html', {'form': form})





@login_required
def profile(request):
    # Assuming you want to show user's details
    return render(request, 'student_management/profile.html', {'user': request.user})

@login_required
def post_search(request):
    query = request.GET.get('search', '')
    posts = Post.objects.filter(
        Q(content__icontains=query),
        visibility='public'
    ) if query else Post.objects.filter(visibility='public')

    return render(request, 'student_management/post_search.html', {
        'posts': posts,
        'search_query': query,
    })

def societies(request):
    societies = Community.objects.filter(is_approved=True)  
    return render(request, 'student_management/societies.html', {'societies': societies})

from rest_framework.views import APIView

class ProtectedEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)