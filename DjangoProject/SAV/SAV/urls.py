# In your SAV/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from Appli_SAV.views import redirect_to_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', LoginView.as_view(next_page='root_redirect'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),  # Removed namespace
    path('', include('Appli_SAV.urls')),
]