from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings  # For AUTH_USER_MODEL

class CustomUser(AbstractUser):
    num_tele = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Client: {self.user.username}"
    
    def crud_demande(self, action, demande=None, **kwargs):
        if action == 'create':
            return f"Demande {kwargs.get('description')} created."
        elif action == 'read':
            return f"Details of demande {demande}"
        elif action == 'update':
            return f"Demande {demande} updated with {kwargs}."
        elif action == 'delete':
            return f"Demande {demande} deleted."

class Technicien(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='technicien_profile')
    specialite = models.CharField(max_length=100)
    avis = models.TextField(blank=True)

    def __str__(self):
        return f"Technicien: {self.user.username}"
    
    def donner_analyse(self, machine):
        return f"Analyse of {machine} by {self.specialite}"

    def crud_machine(self, action, machine=None, **kwargs):
        if action == 'create':
            return f"Machine {kwargs.get('name')} created."
        elif action == 'read':
            return f"Details of machine {machine}"
        elif action == 'update':
            return f"Machine {machine} updated with {kwargs}."
        elif action == 'delete':
            return f"Machine {machine} deleted."

    def donner_prix(self, service, machine_type=None, temps_intervention=None, pieces_remplacees=None):
        tarif_base = 50
        taux_horaire = 30
        prix_pieces = {
            'carte_mere': 120,
            'ecran': 80,
            'clavier': 40,
            'batterie': 60,
        }
        temps_cout = temps_intervention * taux_horaire if temps_intervention else 0
        total_pieces = sum(prix_pieces.get(piece, 0) for piece in pieces_remplacees) if pieces_remplacees else 0
        
        majoration = {
            'ordinateur': 1.0,
            'imprimante': 1.2,
            'serveur': 1.5
        }.get(machine_type, 1.0)

        return round((tarif_base + temps_cout + total_pieces) * majoration, 2)

# Only added machine_type to Machine model (for price calculation)
class Machine(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='machines')
    machine_type = models.CharField(  # Renamed from 'type' for clarity
        max_length=20,
        choices=[
            ('ordinateur', 'Ordinateur'),
            ('imprimante', 'Imprimante'),
            ('serveur', 'Serveur')
        ],
        default='ordinateur'
    )

    def __str__(self):
        return f"{self.machine_type.capitalize()} #{self.id} for {self.client.user.username}"

# DemandeReparation - No changes (kept original fields)
class DemandeReparation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='demandes')
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Demande #{self.id} for {self.machine}"

# ServiceReparation - No changes (kept original fields)
class ServiceReparation(models.Model):
    num_tele = models.CharField(max_length=15)
    demandes = models.ManyToManyField(DemandeReparation, blank=True, related_name='services')

    def __str__(self):
        return f"Service #{self.id}"
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when new user registers"""
    if created:
        if not hasattr(instance, 'client_profile'):
            Client.objects.create(user=instance)