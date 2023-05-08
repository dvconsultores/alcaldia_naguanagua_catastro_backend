from django.contrib import admin
from .models import *
from django.apps import apps

myapp = apps.get_app_config('backend')
for model in myapp.get_models():
    admin.site.register(model)
# Register your models here.