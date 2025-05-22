from django.urls import path
from . import views
from .views import register  # Import from your app's views.py

urlpatterns = [
    # Redirect root URL to client dashboard
    path('', views.redirect_to_client_dashboard, name='root_redirect'),
    
    # Client URLs (French)
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('client/machine/ajouter/', views.ajout_machine, name='ajout_machine'),
    path('client/demande/<int:machine_id>/creer/', views.creer_demande, name='creer_demande'),
    
    # Technician URLs (French)
    path('technicien/', views.technicien_dashboard, name='technicien_dashboard'),
    path('technicien/demande/<int:demande_id>/valider/', views.valider_demande, name='valider_demande'),  # Changed from validate_demande
    path('technicien/demande/<int:demande_id>/prix/', views.calculer_prix, name='calculer_prix'),

    path('register/', register, name='register'),


    path('register/', views.register, name='register'),
]