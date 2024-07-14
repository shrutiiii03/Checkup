from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm, BlogPostForm, AppointmentForm
from .models import User, BlogPost, Appointment
from django.urls import reverse
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from datetime import datetime, timedelta

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            user.user_type = user_type
            if user_type == 'patient':
                user.is_patient = True
                user.is_doctor = False
            elif user_type == 'doctor':
                user.is_patient = False
                user.is_doctor = True
            user.save()
            return redirect(reverse('dashboard:login'))  
    else:
        form = SignupForm()
    return render(request, 'dashboard/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == 'patient':
                    return redirect(reverse('dashboard:patient_dashboard'))
                elif user.user_type == 'doctor':
                    return redirect(reverse('dashboard:doctor_dashboard'))
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def patient_dashboard(request):
    doctors = User.objects.filter(user_type='doctor')
    return render(request, 'dashboard/patient_dashboard.html', {'user': request.user, 'doctors': doctors})

@login_required
def doctor_dashboard(request):
    return render(request, 'dashboard/doctor_dashboard.html', {'user': request.user})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('dashboard:blog_post_list')
    else:
        form = BlogPostForm()
    return render(request, 'dashboard/blog_post_form.html', {'form': form})

@login_required
def blog_post_list(request):
    if request.user.is_doctor:
        posts = BlogPost.objects.filter(author=request.user)
    else:
        posts = BlogPost.objects.filter(is_draft=False)
    
    category = request.GET.get('category')
    if category:
        posts = posts.filter(category=category)

    for post in posts:
        post.summary = ' '.join(post.summary.split()[:15]) + ('...' if len(post.summary.split()) > 15 else '')

    context = {
        'posts': posts,
        'categories': BlogPost.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/blog_post_list.html', context)

@login_required
def blog_post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'dashboard/blog_post_detail.html', {'post': post})

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(doctor, appointment):
    try:
        service = get_google_calendar_service()
        appointment_date = appointment.date        
        start_time = datetime.combine(appointment_date, appointment.start_time)
        print(appointment.patient.username)
        print(doctor.email)
        print(appointment.patient.email)
        event = {
         'summary': 'Appointment with {}'.format(appointment.patient.username),
         'description': 'Appointment details',
            'start': {
                'dateTime': appointment.start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': appointment.end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': doctor.email},
                {'email': appointment.patient.email},
            ],
            
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except HttpError as error:
        print(f'An error occurred: {error}')
                      
@login_required
def book_appointment(request, doctor_id):
    print("Book appointment view accessed")
    doctor = get_object_or_404(User, id=doctor_id, is_doctor=True)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doctor
            appointment.save()
            print("Appointment saved")
          
            try:
                create_calendar_event(doctor, appointment)
            except Exception as error:
                print('An error occurred: %s' % error)
                return render(request, 'dashboard/book_appointment.html', {
                    'form': form,
                    'doctor': doctor,
                    'error': 'There was an issue creating the calendar event. Please ensure email addresses are correct.'
                })

            print("Redirecting to appointment confirm")
            return redirect('dashboard:appointment_confirm', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'dashboard/book_appointment.html', {'form': form, 'doctor': doctor})

@login_required
def appointment_confirm(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'dashboard/appointment_confirm.html', {'appointment': appointment})
