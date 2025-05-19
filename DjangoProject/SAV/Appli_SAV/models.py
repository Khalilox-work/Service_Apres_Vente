from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  

class CustomUser(AbstractUser):

    num_tele = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

# Client
class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Client: {self.user.username}"

 # Technicien
class Technicien(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='technicien_profile')
    specialite = models.CharField(max_length=100)
    avis = models.TextField(blank=True)

    def __str__(self):
        return f"Technicien: {self.user.username}"

# Machine
class Machine(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='machines')

    def __str__(self):
        return f"Machine #{self.id} for {self.client.user.username}"

# Demand Reparation
class DemandeReparation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='demandes')
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Demande #{self.id} for Machine #{self.machine.id}"

# Service Reparation
class ServiceReparation(models.Model):
    num_tele = models.CharField(max_length=15)
    demandes = models.ManyToManyField(DemandeReparation, blank=True, related_name='services')

    def __str__(self):
        return f"Service #{self.id}"