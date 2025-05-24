from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from .models import Machine, DemandeReparation, Technicien, Client
from .forms import MachineForm, DemandeReparationForm, PriceCalculationForm


# ======================
# VUES CLIENT
# ======================

def redirect_to_client_dashboard(request):
    """Redirection vers le tableau de bord client"""
    if hasattr(request.user, 'client_profile'):
        return redirect('client_dashboard')
    return redirect('login')
    

@login_required
def client_dashboard(request):
    try:
        client = request.user.client_profile
    except AttributeError:
        messages.error(request, "Accès réservé aux clients")
        return redirect('login')
    
    machines = client.machines.all()
    demandes = DemandeReparation.objects.filter(machine__client=client)
    return render(request, 'client/dashboard.html', {
        'machines': machines,
        'demandes': demandes
    })

@login_required
def ajout_machine(request):
    """Ajouter une nouvelle machine"""
    try:
        client = request.user.client_profile
    except AttributeError:
        messages.error(request, "Accès réservé aux clients")
        return redirect('login')

    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.client = client
            machine.save()
            messages.success(request, 'Machine enregistrée avec succès!')
            return redirect('client_dashboard')
    else:
        form = MachineForm()
    return render(request, 'client/ajout_machine.html', {'form': form})

@login_required
def creer_demande(request, machine_id):
    """Créer une demande de réparation"""
    try:
        client = request.user.client_profile
    except AttributeError:
        messages.error(request, "Accès réservé aux clients")
        return redirect('login')

    machine = get_object_or_404(Machine, id=machine_id, client=client)
    
    if request.method == 'POST':
        form = DemandeReparationForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.machine = machine
            demande.save()
            messages.success(request, 'Demande créée avec succès!')
            return redirect('client_dashboard')
    else:
        form = DemandeReparationForm()
    return render(request, 'client/creer_demande.html', {
        'form': form,
        'machine': machine
    })

# ======================
# VUES TECHNICIEN
# ======================

@login_required
def technicien_dashboard(request):
    """Tableau de bord technicien"""
    if not hasattr(request.user, 'technicien_profile'):
        messages.error(request, "Accès réservé aux techniciens")
        return redirect('login')
    
    demandes_en_attente = DemandeReparation.objects.filter(date_validation__isnull=True)
    return render(request, 'technicien/dashboard.html', {
        'pending_requests': demandes_en_attente
    })

@login_required
def valider_demande(request, demande_id):
    """Valider une demande de réparation"""
    if not hasattr(request.user, 'technicien_profile'):
        messages.error(request, "Accès réservé aux techniciens")
        return redirect('login')

    demande = get_object_or_404(DemandeReparation, id=demande_id)
    if request.method == 'POST':
        demande.date_validation = timezone.now()
        demande.save()
        messages.success(request, 'Demande validée avec succès!')
        return redirect('technicien_dashboard')
    return render(request, 'technicien/valider_demande.html', {
        'demande': demande
    })

@login_required
def calculer_prix(request, demande_id):
    """Calculer le prix de réparation"""
    if not hasattr(request.user, 'technicien_profile'):
        messages.error(request, "Accès réservé aux techniciens")
        return redirect('login')

    technicien = request.user.technicien_profile
    demande = get_object_or_404(DemandeReparation, id=demande_id)
    
    if request.method == 'POST':
        form = PriceCalculationForm(request.POST)
        if form.is_valid():
            prix = technicien.donner_prix(
                machine_type=demande.machine.machine_type,
                temps_intervention=form.cleaned_data['hours_needed'],
                pieces_remplacees=form.cleaned_data['parts_needed']
            )
            return render(request, 'technicien/prix.html', {
                'price': prix,
                'demande': demande
            })
    else:
        form = PriceCalculationForm()
    return render(request, 'technicien/prix.html', {
        'form': form,
        'demande': demande
    })

# ======================
# VUES PARTAGÉES
# ======================

@login_required
def view_demande(request, demande_id):
    """Voir les détails d'une demande"""
    demande = get_object_or_404(DemandeReparation, id=demande_id)
    if not (request.user == demande.machine.client.user or 
            hasattr(request.user, 'technicien_profile')):
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    return render(request, 'view_demande.html', {
        'demande': demande
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('client_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
    