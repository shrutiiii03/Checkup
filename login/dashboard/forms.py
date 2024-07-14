from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User,BlogPost,Appointment, User
from datetime import datetime

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False) 
    address_line1 = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=50, required=True)
    state = forms.CharField(max_length=50, required=True)
    pincode = forms.CharField(max_length=10, required=True)
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    specialty = forms.CharField(max_length=255, required=False, help_text='Required for doctors')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_picture', 'address_line1', 'city', 'state', 'pincode', 'password1', 'password2', 'user_type','specialty']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if (password1 and password2) and (password1 != password2):
            self.add_error('password2', "Passwords do not match")

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'category', 'summary', 'content', 'is_draft']
        
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'start_time']

    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(is_doctor=True),
        empty_label="Select Doctor"
    )
    date = forms.DateField(
        widget=forms.SelectDateWidget,
        label='Appointment Date'
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        label='Start Time'
    )

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')

        if date and start_time:
            appointment_datetime = datetime.combine(date, start_time)
            if appointment_datetime < datetime.now():
                raise forms.ValidationError("The appointment cannot be in the past.")
        
        return cleaned_data