from django.contrib import admin
from .models import Schema, Service, BindedService, CmwUser, Federations

# Register your models here.
admin.site.register(Schema)
admin.site.register(Service)
admin.site.register(BindedService)
admin.site.register(CmwUser)
admin.site.register(Federations)