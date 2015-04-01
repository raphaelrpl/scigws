from django.contrib import admin
from models import ServiceContact, ServiceProvider, ServiceIdentification, Profile

admin.site.register(ServiceContact)
admin.site.register(ServiceIdentification)
admin.site.register(ServiceProvider)
admin.site.register(Profile)