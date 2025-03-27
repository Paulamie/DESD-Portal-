from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm,CommunityForm
from django.contrib.auth.decorators import login_required
from .models import Event,EventDetails,User
from django.contrib import messages
# from django.conf import settings  # import settings to access AUTH_USER_MODEL


def homepage(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect logged-in users to home
    return render(request, 'student_management/index.html')

@login_required
def home(request):
    return render(request, 'student_management/home.html')

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
    #get all the events and order by start date and time in chronlogical order
    events = Event.objects.all().order_by('start_time')    
    return render(request, 'student_management/event.html', {'events': events})

# class EventListView(ListView):
#     model = Event
#     context_object_name = 'events'  
#     template_name = 'student_management/event.html'  

def community(request):
    return render(request,'student_management/community.html')

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

def communityform(request):
    if request.method == 'POST':
        details = CommunityForm(request.POST)
        if details.is_valid():
            post = details.save(commit=False)
            post.requester = request.user  
            post.save()
            details.save_m2m() 
            messages.success(request, "Your request has been submitted!")
            return(redirect('community'))
        else:
            return render(request, "student_management/community_form.html", {'form': details})
    else:
        form = CommunityForm()
        return render(request, "student_management/community_form.html", {'form': form})

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token


# # Example of a protected view using JWT authentication
# class Home(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         content = {'message': 'Hello, World!'}
#         return Response(content)

# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token

# class CustomAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)

#         return Response({
#             'token': token.key,
#             'user_id': user.user_id,  # Use `user_id` instead of `id` if it's your custom field
#             'email': user.email
#         })

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import UserProfile, Interest, Societies, Community, Friendship
# from .forms import UserUpdateForm, ProfileUpdateForm


# @login_required
# def profile(request):
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)

#     if request.method == "POST":
#         user_form = UserUpdateForm(request.POST, instance=request.user)
#         profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return redirect('profile')
#     else:
#         user_form = UserUpdateForm(instance=request.user)
#         profile_form = ProfileUpdateForm(instance=user_profile)

#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'friends': Friendship.objects.filter(user=request.user),
#         'clubs': user_profile.clubs.all(),
#         'communities': user_profile.communities,  # Fixed: no `.all()` since it's a ForeignKey
#     }
#     return render(request, 'student_management/profile.html', context)

