# Generated by Django 5.0.6 on 2024-07-04 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_user_address_line1_user_city_user_pincode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('patient', 'Patient'), ('doctor', 'Doctor')], default='patient', max_length=10),
        ),
    ]
