from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import register

urlpatterns = [
    # Redirect root URL to appropriate dashboard
    path('', views.redirect_to_dashboard, name='root_redirect'),
    
    # Client URLs (French)
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('client/machine/ajouter/', views.ajout_machine, name='ajout_machine'),
    path('client/demande/<int:machine_id>/creer/', views.creer_demande, name='creer_demande'),
    
    # Technician URLs (French)
    path('technicien/', views.technicien_dashboard, name='technicien_dashboard'),
    path('technicien/historique/', views.historique_reparations, name='historique_reparations'),
    path('technicien/demande/<int:demande_id>/valider/', views.valider_demande, name='valider_demande'),
    path('technicien/demande/<int:demande_id>/prix/', views.calculer_prix, name='calculer_prix'),
    
    # Admin URLs (renamed to avoid conflict with Django admin)
    path('tableau-de-bord-admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Authentication URLs
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Shared URLs
    path('demande/<int:demande_id>/', views.view_demande, name='view_demande'),
]