from django.db import models
from .constants import LEVEL_CHOICES
    
# Create your models here.

class CmwUser(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username
    
    def to_dict(self) -> dict:
        dictionary = {}
        dictionary["username"] = self.username
        dictionary["password"] = self.password
        if self.admin:
            dictionary["tags"] = ["administrator"] 
        return dictionary
    
class Service(models.Model):
    name = models.CharField(verbose_name="Service's Vhost name", max_length=50)
    normal_user = models.OneToOneField(CmwUser, related_name='normal_user', on_delete=models.DO_NOTHING)
    federation_user = models.OneToOneField(CmwUser, related_name='federation_user', on_delete=models.DO_NOTHING)
    shovel_user = models.OneToOneField(CmwUser, related_name='shovel_user', on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.name

class BindedService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    mqtt_input_enabled = models.BooleanField(default=False)
    mqtt_output_enabled = models.BooleanField(default=False)
    mqtt_binding_routing_keys = models.TextField(max_length=500) 

    def __str__(self) -> str:
        return f"{self.service.name}_{self.pk}"

class Schema(models.Model):
    name = models.CharField(verbose_name="Cluster Name", max_length=50)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=20)
    version = models.CharField(verbose_name="RabbitMQ version used", max_length=10) #TODO make sure it has version format
    binded_services = models.ManyToManyField(BindedService)
    aditional_users = models.ManyToManyField(CmwUser, blank=True)

    def __str__(self) -> str:
        return self.name
    

class Federations(models.Model):
    name = models.CharField(verbose_name="Federation Name", max_length=50)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    destination_level = models.CharField(choices=LEVEL_CHOICES, max_length=20)
    federations_binding_routing_keys = models.TextField(max_length=500)  
    hostname = models.CharField(max_length=150)
    port = models.IntegerField()
    max_hops = models.IntegerField()

    def __str__(self) -> str:
        return self.name
