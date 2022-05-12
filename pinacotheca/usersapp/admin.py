from django.contrib import admin
from usersapp.models import UserAccount
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models

admin.site.register(UserAccount)
# Register your models here.
