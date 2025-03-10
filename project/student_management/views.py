from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout 
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from .models import Event,EventDetails

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
    #get all the events 
    events = Event.objects.all()  
    return render(request, 'student_management/event.html', {'events': events})

# def event_detail(request,user_id):
# #     # booked = EventDetails.objects.all() (this would get it for all)
# #     booked= EventDetails.objects.get(user=request.user) #gets the specific event details for a specific user
# #     event = Event.objects.filter(event_id=event_id).first() 
# #     booked= EventDetails.objects.filter(user_id=user_id).select_related("event")
# #     # return render(request, "event_details.html", {"event": event,"booked_users": booked_users,})
# #     return render(request,"booked_events.html", {'booked': booked})

#     booked= EventDetails.objects.select_related('event').filter(user_id=user_id)
#     return render(request,"booked_events.html", {'booked': booked})
# #would join the EventDetails table with events (select_related)
# #filter would take the user_id 