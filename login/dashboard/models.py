from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta, time

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    specialty = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user_type == 'patient':
            self.is_patient = True
            self.is_doctor = False
        elif self.user_type == 'doctor':
            self.is_patient = False
            self.is_doctor = True
        print(f"Saving User: {self.username}, Type: {self.user_type}, is_patient: {self.is_patient}, is_doctor: {self.is_doctor}")  # Debugging statement
        super(User, self).save(*args, **kwargs)



from django.contrib.auth import get_user_model
User = get_user_model()

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('Mental Health', 'Mental Health'),
        ('Heart Disease', 'Heart Disease'),
        ('Covid19', 'Covid19'),
        ('Immunization', 'Immunization'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    summary = models.TextField()
    content = models.TextField()
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_doctor', limit_choices_to={'is_doctor': True})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(editable=False) 

    def save(self, *args, **kwargs):
        
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + timedelta(minutes=45)
        self.end_time = end_datetime.time()
        print(f"Start datetime: {start_datetime}")
        print(f"End datetime: {end_datetime}")
        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} on {self.date} at {self.start_time}"