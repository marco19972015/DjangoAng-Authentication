 
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# We extend User class using AbstractUser from Django
class User(AbstractUser):
    # All of the variables below are configured through AbstractUser
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # each user should have a unique email so we set that to True
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    # username is a field abstractuser and we don't want to log in using username, we want to log in using email
    username = None

    # then we set the username_field equal to email (Specifies which model field is going to be used as the username)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []