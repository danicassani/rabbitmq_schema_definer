from django.contrib import admin
from .models import Schema, Service, BindedService, MqUser, Federations

# Register your models here.
admin.site.register(Schema)
admin.site.register(Service)
admin.site.register(BindedService)
admin.site.register(MqUser)
admin.site.register(Federations)