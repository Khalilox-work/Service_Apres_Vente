from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Machine, DemandeReparation, CustomUser, Technicien

# Machine Form (for clients to register machines)
class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['machine_type']  # Only show machine_type (client is auto-assigned)
        
        labels = {
            'machine_type': 'Machine Type'
        }
        help_texts = {
            'machine_type': 'Select the type of device needing repair'
        }

# Repair Request Form (for clients to submit issues)
class DemandeReparationForm(forms.ModelForm):
    class Meta:
        model = DemandeReparation
        fields = ['description']  # machine is assigned in the view
        
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Describe the problem in detail...'
            })
        }
        labels = {
            'description': 'Problem Description'
        }

# Custom Registration Form
class CustomRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('technicien', 'Technicien')
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label='Type de Compte',
        initial='client'
    )
    
    specialite = forms.CharField(
        max_length=100,
        required=False,
        label='Spécialité (Pour les techniciens)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Réparation ordinateurs, Imprimantes, etc.'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'num_tele')
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        specialite = cleaned_data.get('specialite')
        
        if role == 'technicien' and not specialite:
            raise forms.ValidationError(
                "La spécialité est requise pour les comptes techniciens."
            )
        return cleaned_data

# Price Calculator Form (for technicians)
class PriceCalculationForm(forms.Form):
    hours_needed = forms.FloatField(
        min_value=0.5,
        max_value=24,
        widget=forms.NumberInput(attrs={
            'step': '0.5',
            'class': 'form-control',
            'placeholder': 'Estimated repair time in hours'
        }),
        label='Labor Hours Required'
    )
    
    PARTS_CHOICES = [
        ('carte_mere', 'Motherboard (€120)'),
        ('ecran', 'Screen (€80)'),
        ('batterie', 'Battery (€60)'),
        ('clavier', 'Keyboard (€40)'),
    ]
    
    parts_needed = forms.MultipleChoiceField(
        choices=PARTS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Replacement Parts',
        required=False
    )