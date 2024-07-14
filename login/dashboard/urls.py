# dashboard/urls.py

from django.urls import path
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('create_blog_post/', views.create_blog_post, name='create_blog_post'),
    path('blog_post_list/', views.blog_post_list, name='blog_post_list'),
    path('blog_post_detail/<int:pk>/', views.blog_post_detail, name='blog_post_detail'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('appointment-confirm/<int:appointment_id>/', views.appointment_confirm, name='appointment_confirm'),
]


