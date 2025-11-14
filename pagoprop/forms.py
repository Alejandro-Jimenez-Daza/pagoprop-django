from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Comprobante, Apartamento

# Formulario de Registro
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombres'
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apellidos'
    }))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Usuario'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar contraseña'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


# Formulario de Login
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))


# Formulario para subir comprobantes
class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['apartamento', 'archivo', 'monto']
        widgets = {
            'apartamento': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*,application/pdf'
            }),
            'monto': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 1.200.000', 
                'inputmode': 'numeric'
            }),
        }
        labels = {
            'apartamento': 'Selecciona tu apartamento',
            'archivo': 'Comprobante (imagen o PDF)',
            'monto': 'Monto pagado',
        }
    
    def __init__(self, user, *args, **kwargs):
        super(ComprobanteForm, self).__init__(*args, **kwargs)
        # Filtrar solo apartamentos del usuario logueado
        self.fields['apartamento'].queryset = user.apartamentos.all()

        #EDITANDO TIENE INSTANCE, EL ARCHIVO SE HACE OPCIONAL
        if self.instance and self.instance.pk:
            self.fields['archivo'].required = False


        