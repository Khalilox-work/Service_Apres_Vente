from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # For AUTH_USER_MODEL

class CustomUser(AbstractUser):
    # Remove `nom` and `prenom` (use built-in `first_name` and `last_name`)
    num_tele = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

# Client Model (linked to CustomUser via AUTH_USER_MODEL)
class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Client: {self.user.username}"
    
    def crud_demande(self, action, demande=None, **kwargs):
        if action == 'create':
            # Create a new demande
            return f"Demande {kwargs.get('description')} created."
        elif action == 'read':
            # Read demande information
            return f"Details of demande {demande}"
        elif action == 'update':
            # Update demande information
            return f"Demande {demande} updated with {kwargs}."
        elif action == 'delete':
            # Delete demande
            return f"Demande {demande} deleted."


# Technicien Model (linked to CustomUser)
class Technicien(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='technicien_profile')
    specialite = models.CharField(max_length=100)
    avis = models.TextField(blank=True)

    def __str__(self):
        return f"Technicien: {self.user.username}"
    
    def donner_analyse(self, machine):
        # Logic for analyzing a machine
        return f"Analyse of {machine} by {self.specialite}"

    def crud_machine(self, action, machine=None, **kwargs):
        if action == 'create':
            # Create a new machine (dummy logic)
            return f"Machine {kwargs.get('name')} created."
        elif action == 'read':
            # Read machine information
            return f"Details of machine {machine}"
        elif action == 'update':
            # Update machine information
            return f"Machine {machine} updated with {kwargs}."
        elif action == 'delete':
            # Delete machine
            return f"Machine {machine} deleted."

    def donner_prix(self, service):
        # Logic to calculate price for a service
        return f"Price for {service} calculated."
    


# Machine Model
class Machine(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='machines')

    def __str__(self):
        return f"Machine #{self.id} for {self.client.user.username}"

# DemandeReparation Model
class DemandeReparation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='demandes')
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Demande #{self.id} for Machine #{self.machine.id}"

# ServiceReparation Model
class ServiceReparation(models.Model):
    num_tele = models.CharField(max_length=15)
    demandes = models.ManyToManyField(DemandeReparation, blank=True, related_name='services')

    def __str__(self):
        return f"Service #{self.id}"