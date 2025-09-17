from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    Usuario, Lugar, Mision, Territorio,
    Regalo, RegaloEnviado, Amistad,
    Articulo, SalonAmigos, CuartoSalon, SalonArticulo
)

# ------------------------
# FORMULARIOS DE ADMIN
# ------------------------
class SolicitarCodigoAdminForm(forms.Form):
    correo = forms.EmailField(label="Tu correo registrado")

class IngresarCodigoAdminForm(forms.Form):
    codigo = forms.CharField(max_length=100, label="Ingresa tu código de administrador")

# ------------------------
# FORMULARIOS DE REGISTRO
# ------------------------
class RegistroForm(UserCreationForm):
    correo = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = Usuario
        fields = ['username', 'correo', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar clases CSS a todos los campos
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg rounded-3'
            })

# ------------------------
# FORMULARIOS DE USUARIOS
# ------------------------
class UsuarioCreationForm(UserCreationForm):
    admin_code = forms.CharField(
        max_length=50,
        required=False,
        label="Código de administrador (opcional)",
        help_text="Ingresa este código solo si quieres obtener permisos de administrador."
    )

    class Meta:
        model = Usuario
        fields = ("username", "correo", "rol", "password1", "password2", "admin_code")
        labels = {
            "username": "Nombre de usuario",
            "correo": "Correo electrónico",
            "rol": "Rol",
            "password1": "Contraseña",
            "password2": "Confirmar contraseña",
        }
        help_texts = {
            "username": "Máximo 150 caracteres. Letras, números y @/./+/-/_ solamente.",
            "password1": (
                "Tu contraseña debe tener al menos 8 caracteres, no puede ser demasiado común, "
                "no puede ser solo números y no debe ser similar a tu información personal."
            ),
        }

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ["username", "correo", "rol"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-select"}),
        }

# ------------------------
# FORMULARIOS DE LUGARES
# ------------------------
class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre", "descripcion", "ubicacion", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del lugar"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ubicación"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

# ------------------------
# FORMULARIOS DE MISIONES
# ------------------------
class MisionForm(forms.ModelForm):
    class Meta:
        model = Mision
        fields = ["titulo", "descripcion", "lugar", "minijuego_enlace", "imagen"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "lugar": forms.Select(attrs={"class": "form-select"}),
            "minijuego_enlace": forms.TextInput(attrs={"class": "form-control", "placeholder": "URL del minijuego"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

# ------------------------
# FORMULARIOS DE ARTÍCULOS
# ------------------------
class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ["nombre", "descripcion", "precio"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

# ------------------------
# FORMULARIOS DE TERRITORIOS
# ------------------------
class TerritorioForm(forms.ModelForm):
    class Meta:
        model = Territorio
        fields = ["nombre", "descripcion", "estado", "puntos"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "puntos": forms.NumberInput(attrs={"class": "form-control"}),
        }

# ------------------------
# FORMULARIOS DE AMISTADES
# ------------------------
class AmistadForm(forms.ModelForm):
    class Meta:
        model = Amistad
        fields = ["remitente", "destinatario", "estado"]
        widgets = {
            "remitente": forms.Select(attrs={"class": "form-select"}),
            "destinatario": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

# ------------------------
# FORMULARIOS DE REGALOS
# ------------------------
class RegaloForm(forms.ModelForm):
    class Meta:
        model = Regalo
        fields = ["nombre", "descripcion", "puntos_bonus"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "puntos_bonus": forms.NumberInput(attrs={"class": "form-control"}),
        }

class RegaloEnviadoForm(forms.ModelForm):
    class Meta:
        model = RegaloEnviado
        fields = ["regalo", "de_usuario", "para_usuario"]
        widgets = {
            "regalo": forms.Select(attrs={"class": "form-select"}),
            "de_usuario": forms.Select(attrs={"class": "form-select"}),
            "para_usuario": forms.Select(attrs={"class": "form-select"}),
        }

# ------------------------
# FORMULARIOS DE SALONES
# ------------------------
class SalonAmigosForm(forms.ModelForm):
    class Meta:
        model = SalonAmigos
        fields = ["nombre", "propietario"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "propietario": forms.Select(attrs={"class": "form-select"}),
        }

class CuartoSalonForm(forms.ModelForm):
    class Meta:
        model = CuartoSalon
        fields = ["salon", "nombre"]
        widgets = {
            "salon": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
        }

class SalonArticuloForm(forms.ModelForm):
    class Meta:
        model = SalonArticulo
        fields = ["salon", "articulo", "cantidad"]
        widgets = {
            "salon": forms.Select(attrs={"class": "form-select"}),
            "articulo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
        }
