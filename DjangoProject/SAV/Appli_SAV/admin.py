from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Client, Technicien, Machine, DemandeReparation, ServiceReparation

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'num_tele', 'email', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'num_tele')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Technicien)
admin.site.register(Machine)
admin.site.register(DemandeReparation)
admin.site.register(ServiceReparation)