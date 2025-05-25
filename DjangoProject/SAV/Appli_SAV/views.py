from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Machine, DemandeReparation, Technicien, Client
from .forms import MachineForm, DemandeReparationForm, PriceCalculationForm, CustomRegistrationForm
from django.db.models import Count, Q
from datetime import timedelta
from django.db import models


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
    """Dashboard for clients"""
    # First check if user is a technician and redirect if so
    if hasattr(request.user, 'technicien_profile'):
        return redirect('technicien_dashboard')
    
    try:
        client = request.user.client_profile
    except AttributeError:
        messages.error(request, "Accès réservé aux clients")
        return redirect('root_redirect')
    
    machines = client.machines.all()
    demandes = DemandeReparation.objects.filter(machine__client=client)
    
    # Calculate validated requests count
    validated_count = demandes.filter(date_validation__isnull=False).count()
    
    # Calculate total cost
    total_cost = demandes.filter(prix__isnull=False).aggregate(
        total=models.Sum('prix')
    )['total'] or 0
    
    return render(request, 'client/dashboard.html', {
        'machines': machines,
        'demandes': demandes,
        'current_date': timezone.now(),
        'validated_count': validated_count,
        'total_cost': total_cost
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
    return render(request, 'client/ajout_machine.html', {
        'form': form,
        'current_date': timezone.now()
    })

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
        'machine': machine,
        'current_date': timezone.now()
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
    
    # Get pending requests
    demandes_en_attente = DemandeReparation.objects.filter(date_validation__isnull=True)
    
    # Get validated requests count
    validated_count = DemandeReparation.objects.filter(date_validation__isnull=False).count()
    
    # Get total interventions (all requests)
    total_interventions = DemandeReparation.objects.count()
    
    return render(request, 'technicien/dashboard.html', {
        'pending_requests': demandes_en_attente,
        'validated_count': validated_count,
        'total_interventions': total_interventions,
        'current_date': timezone.now(),
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
            # Save the calculated price
            demande.prix = prix
            demande.save()
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

@login_required
def historique_reparations(request):
    """Historique des réparations pour un technicien"""
    if not hasattr(request.user, 'technicien_profile'):
        messages.error(request, "Accès réservé aux techniciens")
        return redirect('login')

    # Get all validated repairs for this technician
    reparations = DemandeReparation.objects.filter(
        date_validation__isnull=False
    ).order_by('-date_validation')

    # Calculate total interventions
    total_interventions = reparations.count()

    # Calculate this month's interventions
    current_month = timezone.now().month
    month_interventions = reparations.filter(
        date_validation__month=current_month
    ).count()

    # Calculate average repair time
    avg_time = reparations.annotate(
        duree_reparation=models.ExpressionWrapper(
            models.F('date_validation') - models.F('date_creation'),
            output_field=models.DurationField()
        )
    ).aggregate(
        avg_duration=models.Avg('duree_reparation')
    )['avg_duration']

    avg_time = round(avg_time.days if avg_time else 0, 1) if avg_time else 0

    # Calculate total revenue
    total_revenue = reparations.aggregate(
        total=models.Sum('prix')
    )['total'] or 0

    # Add duration to each repair
    for reparation in reparations:
        duration = reparation.date_validation - reparation.date_creation
        reparation.duree_reparation = duration.days

    return render(request, 'technicien/historique_reparations.html', {
        'reparations': reparations,
        'total_interventions': total_interventions,
        'month_interventions': month_interventions,
        'avg_time': avg_time,
        'total_revenue': total_revenue,
        'current_date': timezone.now()
    })

# ======================
# VUES PARTAGÉES
# ======================

def redirect_to_dashboard(request):
    """Redirection vers le tableau de bord approprié selon le rôle"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if hasattr(request.user, 'client_profile'):
        return redirect('client_dashboard')
    elif hasattr(request.user, 'technicien_profile'):
        return redirect('technicien_dashboard')
    elif request.user.is_staff:  # For admin users
        return redirect('admin_dashboard')
    else:
        messages.warning(request, "Votre compte n'a pas de rôle assigné.")
        return redirect('login')

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
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            
            if role == 'technicien':
                # Create technician profile
                Technicien.objects.create(
                    user=user,
                    specialite=form.cleaned_data['specialite']
                )
                messages.success(request, 'Compte technicien créé avec succès!')
            else:  # role == 'client'
                # Client profile will be created by the signal
                messages.success(request, 'Compte client créé avec succès!')
            
            # Log the user in and redirect
            login(request, user)
            return redirect('root_redirect')
    else:
        form = CustomRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# ======================
# VUES ADMIN
# ======================

@login_required
def admin_dashboard(request):
    """Tableau de bord administrateur"""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('login')
    
    # Basic statistics
    clients_count = Client.objects.count()
    techniciens_count = Technicien.objects.count()
    machines_count = Machine.objects.count()
    demandes_count = DemandeReparation.objects.count()
    demandes_en_attente = DemandeReparation.objects.filter(date_validation__isnull=True).count()
    
    # Calculate percentages
    if demandes_count > 0:
        pending_percent = (demandes_en_attente / demandes_count) * 100
        completed_percent = 100 - pending_percent
    else:
        pending_percent = 0
        completed_percent = 0
    
    # Machine types distribution
    machine_types = Machine.objects.values('machine_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent activity
    User = get_user_model()
    recent_demandes = DemandeReparation.objects.select_related(
        'machine', 'machine__client', 'machine__client__user'
    ).order_by('-date_creation')[:5]
    recent_users = User.objects.prefetch_related(
        'client_profile', 'technicien_profile'
    ).order_by('-date_joined')[:5]
    
    # Weekly statistics
    week_ago = timezone.now() - timedelta(days=7)
    new_clients_week = Client.objects.filter(
        user__date_joined__gte=week_ago
    ).count()
    new_demandes_week = DemandeReparation.objects.filter(
        date_creation__gte=week_ago
    ).count()
    
    return render(request, 'admin/dashboard.html', {
        'stats': {
            'clients': clients_count,
            'techniciens': techniciens_count,
            'machines': machines_count,
            'demandes_total': demandes_count,
            'demandes_en_attente': demandes_en_attente,
            'new_clients_week': new_clients_week,
            'new_demandes_week': new_demandes_week,
            'pending_percent': pending_percent,
            'completed_percent': completed_percent
        },
        'machine_types': machine_types,
        'recent_demandes': recent_demandes,
        'recent_users': recent_users,
        'current_date': timezone.now()
    })
    