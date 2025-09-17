

# =========================
# IMPORTS NECESARIOS
# =========================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail


# =========================
# IMPORTS LOCALES
# =========================
from .models import Usuario
from .forms import UsuarioCreationForm

# =========================
# CONFIGURACIÓN GENERAL
# =========================
from django.conf import settings
import logging
import secrets

# Configuración del email desde settings o valor por defecto
FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

# Logger para registrar eventos importantes
logger = logging.getLogger(__name__)

# ------------------------
# Configuración de administración
# ------------------------
# Código secreto que desbloquea rol de administrador
ADMIN_SECRET_CODE = "TU_CODIGO_SECRETO_AQUI"

# Opcional: listas de emails y contraseñas especiales que también pueden otorgar admin
ADMIN_EMAILS = ["admin@example.com"]
ADMIN_PASSWORDS = ["Password123"]

# ------------------------
# Configuración de tokens de confirmación
# ------------------------
# Longitud y formato de los tokens generados para confirmar cuenta / camuflar admin
CONFIRMATION_TOKEN_LENGTH = 6  # en caracteres hexadecimales


def register(request):
    """
    Registro seguro de usuarios:
    - Rol predeterminado 'jugador'.
    - Genera admin_token (camuflado como 'código de confirmación') y lo envía por email.
    - Si el usuario ingresa ADMIN_SECRET_CODE, se le otorga rol administrador.
    """
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        admin_code = request.POST.get("admin_code", "").strip()[:20]  # limitar tamaño del input

        if form.is_valid():
            usuario = form.save(commit=False)
            
            # Forzar rol por defecto
            usuario.rol = "jugador"

            # Desbloquear admin si el código es correcto
            if admin_code and admin_code == ADMIN_SECRET_CODE:
                usuario.rol = "admin"
                usuario.is_staff = True
                usuario.is_superuser = True
                usuario.llave_seguridad = secrets.token_hex(8)  # llave única
                messages.success(
                    request,
                    f"¡Felicidades! Se te ha concedido rol administrador. Tu llave de seguridad: {usuario.llave_seguridad}"
                )

            # Generar token de confirmación camuflado para evitar bots
            token_confirmacion = secrets.token_hex(3)  # 6 caracteres hexadecimales
            usuario.admin_token = token_confirmacion

            # Opcional: desactivar cuenta hasta confirmar correo
            # usuario.is_active = False

            # Guardar usuario
            usuario.save()

            # Enviar correo con token de confirmación
            try:
                send_mail(
                    subject="Código de confirmación - TourExpress",
                    message=(
                        f"Hola {usuario.username},\n\n"
                        f"Tu código de confirmación es: {token_confirmacion}\n\n"
                        "Este código sirve para confirmar tu cuenta (camuflado para seguridad)."
                    ),
                    from_email=FROM_EMAIL,
                    recipient_list=[usuario.correo],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Error al enviar correo a {usuario.correo}: {e}")
                messages.warning(
                    request,
                    "Registro creado, pero no se pudo enviar el correo de confirmación."
                )

            messages.success(request, "Registro exitoso. Revisa tu correo para el código de confirmación.")
            return redirect("juego:login")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = UsuarioCreationForm()

    return render(request, "juego/register.html", {"form": form})

    

@login_required
def confirmar_codigo(request):
    """
    Vista para que el usuario ingrese el código recibido por correo.
    Al coincidir con user.admin_token, se confirma la cuenta y limpia el token.
    """
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        u = request.user
        if u.admin_token and codigo and codigo == u.admin_token:
            u.admin_token = ""
            # si previamente habías dejado is_active=False al crear, activarlo aquí:
            u.is_active = True
            u.save()
            messages.success(request, "Código correcto. Cuenta confirmada.")
            return redirect("juego:home")
        else:
            messages.error(request, "Código incorrecto.")
    return render(request, "juego/confirmar_codigo.html")

# ==============================
#   ADMIN: CÓDIGO DE CONFIRMACIÓN
# ==============================


@login_required
def ingresar_codigo_admin(request):
    """
    Permite a un jugador ingresar el código recibido para convertirse en admin.
    """
    if request.method == "POST":
        form = IngresarCodigoAdminForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            usuario = request.user
            if usuario.admin_token == codigo:
                usuario.rol = "admin"
                usuario.llave_seguridad = secrets.token_hex(8)  # llave única
                usuario.admin_token = ""  # limpiar token
                usuario.save()
                messages.success(request, f"¡Felicidades! Ahora eres administrador. Tu llave de seguridad: {usuario.llave_seguridad}")
                return redirect("juego:admin_dashboard")
            else:
                messages.error(request, "Código incorrecto")
    else:
        form = IngresarCodigoAdminForm()
    return render(request, "juego/ingresar_codigo.html", {"form": form})


def solicitar_codigo_admin(request):
    """
    Permite a un jugador solicitar un código de admin. 
    Se genera token único y se envía al correo del usuario.
    """
    if request.method == "POST":
        form = SolicitarCodigoAdminForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                usuario = Usuario.objects.get(correo=correo)
                token = secrets.token_hex(4)  # código temporal
                usuario.admin_token = token
                usuario.save()

                # Enviar correo
                send_mail(
                    subject="Tu código de administrador",
                    message=f"Hola {usuario.username}, tu código de administrador es: {token}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[correo],
                )

                messages.success(request, "El código de administrador ha sido enviado a tu correo.")
                return redirect("juego:login")

            except Usuario.DoesNotExist:
                messages.error(request, "Correo no registrado")
    else:
        form = SolicitarCodigoAdminForm()
    return render(request, "juego/solicitar_codigo.html", {"form": form})

# -------------------------------
# IMPORTAR MODELOS
# -------------------------------
from .models import (
    Usuario, Lugar, Mision, Territorio,
    Regalo, RegaloEnviado, Amistad,
    Articulo, SalonAmigos, CuartoSalon, SalonArticulo, Visita
)

# -------------------------------
# IMPORTAR FORMULARIOS
# -------------------------------
from .forms import (
    UsuarioCreationForm, UsuarioChangeForm,
    LugarForm, MisionForm, ArticuloForm,
    TerritorioForm, AmistadForm, RegaloForm, RegaloEnviadoForm,
    SalonAmigosForm, CuartoSalonForm, SalonArticuloForm
)


# ==============================
#   FUNCIONES AUXILIARES
# ==============================
def es_admin(user):
    """Verifica si el usuario es administrador."""
    return user.is_superuser or user.is_staff or user.rol == "admin"

# ==============================
#   AUTENTICACIÓN
# ==============================
def login(request):
    if request.method == "POST":
        login_input = request.POST.get("username")
        password = request.POST.get("password")

        # Buscar usuario por username o email
        try:
            user_obj = Usuario.objects.get(username=login_input)
        except Usuario.DoesNotExist:
            try:
                user_obj = Usuario.objects.get(correo=login_input)
            except Usuario.DoesNotExist:
                user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                auth_login(request, user)

                # Si es admin y no tiene llave, se genera automáticamente
                if user.rol == "admin" and not user.llave_seguridad:
                    user.llave_seguridad = secrets.token_hex(8)
                    user.save()
                    messages.success(request, f"Bienvenido Admin. Tu llave de seguridad: {user.llave_seguridad}")

                # Redirección según rol
                if user.rol == "admin":
                    return redirect("juego:admin_dashboard")
                else:
                    return redirect("juego:home")

        messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "juego/login.html")


@login_required
def logout(request):
    """Cerrar sesión del usuario."""
    auth_logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect("juego:login")


@login_required
def home(request):
    """Home para jugadores normales."""
    return render(request, "juego/home.html")


@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    """Panel de administración."""
    return render(request, "juego/admin/dashboard.html")


# ==============================
#   USUARIOS (CRUD)
# ==============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from juego.models import Usuario
from juego.forms import UsuarioCreationForm, UsuarioChangeForm

def es_admin(user):
    return user.is_superuser or user.is_staff or user.rol == "admin"

@login_required
@user_passes_test(es_admin)
def usuario_list(request):
    usuarios = Usuario.objects.all()
    return render(request, "juego/usuarios/list.html", {"usuarios": usuarios})


@login_required
@user_passes_test(es_admin)
def usuario_create(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado con éxito")
            return redirect("juego:usuario_list")
    else:
        form = UsuarioCreationForm()
    return render(request, "juego/usuarios/form.html", {"form": form, "form_title": "Crear Usuario"})

@login_required
@user_passes_test(es_admin)
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado con éxito")
            return redirect("juego:usuario_list")
    else:
        form = UsuarioChangeForm(instance=usuario)
    return render(request, "juego/usuarios/form.html", {"form": form, "form_title": "Editar Usuario"})

@login_required
@user_passes_test(es_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    messages.success(request, "Usuario eliminado")
    return redirect("juego:usuario_list")


@login_required
@user_passes_test(es_admin)
def usuario_detail(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, "juego/usuarios/detail.html", {"usuario": usuario})


# ==============================
#   CRUD: LUGARES
# ==============================
@login_required
def lugar_list(request):
    lugares = Lugar.objects.all()
    return render(request, "juego/lugares/list.html", {"lugares": lugares})


@login_required
def lugar_create(request):
    if request.method == "POST":
        form = LugarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Lugar creado con éxito")
            return redirect("juego:lugar_list")
    else:
        form = LugarForm()
    return render(request, "juego/lugares/form.html", {"form": form})


@login_required
def lugar_update(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    if request.method == "POST":
        form = LugarForm(request.POST, request.FILES, instance=lugar)
        if form.is_valid():
            form.save()
            messages.success(request, "Lugar actualizado")
            return redirect("juego:lugar_list")
    else:
        form = LugarForm(instance=lugar)
    return render(request, "juego/lugares/form.html", {"form": form})


@login_required
def lugar_delete(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    lugar.delete()
    messages.success(request, "Lugar eliminado")
    return redirect("juego:lugar_list")


@login_required
def lugar_detail(request, pk):
    lugar = get_object_or_404(Lugar, pk=pk)
    return render(request, "juego/lugares/detail.html", {"lugar": lugar})


# ==============================
#   CRUD: MISIONES
# ==============================
@login_required
def mision_list(request):
    misiones = Mision.objects.all()
    return render(request, "juego/misiones/list.html", {"misiones": misiones})


@login_required
def mision_create(request):
    if request.method == "POST":
        form = MisionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Misión creada")
            return redirect("juego:mision_list")
    else:
        form = MisionForm()
    return render(request, "juego/misiones/form.html", {"form": form})


@login_required
def mision_update(request, pk):
    mision = get_object_or_404(Mision, pk=pk)
    if request.method == "POST":
        form = MisionForm(request.POST, request.FILES, instance=mision)
        if form.is_valid():
            form.save()
            messages.success(request, "Misión actualizada")
            return redirect("juego:mision_list")
    else:
        form = MisionForm(instance=mision)
    return render(request, "juego/misiones/form.html", {"form": form})


@login_required
def mision_delete(request, pk):
    mision = get_object_or_404(Mision, pk=pk)
    mision.delete()
    messages.success(request, "Misión eliminada")
    return redirect("juego:mision_list")


@login_required
def mision_detail(request, pk):
    mision = get_object_or_404(Mision, pk=pk)
    return render(request, "juego/misiones/detail.html", {"mision": mision})


# ==============================
#   CRUD: ARTÍCULOS
# ==============================
@login_required
def articulo_list(request):
    articulos = Articulo.objects.all()
    return render(request, "juego/articulos/list.html", {"articulos": articulos})


@login_required
def articulo_create(request):
    if request.method == "POST":
        form = ArticuloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Artículo creado")
            return redirect("juego:articulo_list")
    else:
        form = ArticuloForm()
    return render(request, "juego/articulos/form.html", {"form": form})


@login_required
def articulo_update(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    if request.method == "POST":
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, "Artículo actualizado")
            return redirect("juego:articulo_list")
    else:
        form = ArticuloForm(instance=articulo)
    return render(request, "juego/articulos/form.html", {"form": form})


@login_required
def articulo_delete(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    articulo.delete()
    messages.success(request, "Artículo eliminado")
    return redirect("juego:articulo_list")


@login_required
def articulo_detail(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    return render(request, "juego/articulos/detail.html", {"articulo": articulo})


# ==============================
#   CRUD: TERRITORIOS
# ==============================
@login_required
def territorio_list(request):
    territorios = Territorio.objects.all()
    return render(request, "juego/territorios/list.html", {"territorios": territorios})


@login_required
def territorio_create(request):
    if request.method == "POST":
        form = TerritorioForm(request.POST)
        if form.is_valid():
            territorio = form.save(commit=False)
            territorio.propietario = request.user
            territorio.save()
            messages.success(request, "Territorio creado")
            return redirect("juego:territorio_list")
    else:
        form = TerritorioForm()
    return render(request, "juego/territorios/form.html", {"form": form})


@login_required
def territorio_update(request, pk):
    territorio = get_object_or_404(Territorio, pk=pk)
    if request.method == "POST":
        form = TerritorioForm(request.POST, instance=territorio)
        if form.is_valid():
            form.save()
            messages.success(request, "Territorio actualizado")
            return redirect("juego:territorio_list")
    else:
        form = TerritorioForm(instance=territorio)
    return render(request, "juego/territorios/form.html", {"form": form})


@login_required
def territorio_delete(request, pk):
    territorio = get_object_or_404(Territorio, pk=pk)
    territorio.delete()
    messages.success(request, "Territorio eliminado")
    return redirect("juego:territorio_list")


@login_required
def territorio_detail(request, pk):
    territorio = get_object_or_404(Territorio, pk=pk)
    visitas = Visita.objects.filter(territorio=territorio)
    return render(request, "juego/territorios/detail.html", {"territorio": territorio, "visitas": visitas})


@login_required
def visitar_territorio(request, pk):
    territorio = get_object_or_404(Territorio, pk=pk)
    Visita.objects.create(visitante=request.user, territorio=territorio)
    messages.success(request, f"Has visitado {territorio.nombre}")
    return redirect("juego:territorio_detail", pk=pk)


# ==============================
#   CRUD: AMISTADES
# ==============================
@login_required
def amistad_list(request):
    amistades = Amistad.objects.all()
    return render(request, "juego/amistades/list.html", {"amistades": amistades})


@login_required
def amistad_create(request):
    if request.method == "POST":
        form = AmistadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud de amistad enviada")
            return redirect("juego:amistad_list")
    else:
        form = AmistadForm()
    return render(request, "juego/amistades/form.html", {"form": form})


@login_required
def amistad_update(request, pk):
    amistad = get_object_or_404(Amistad, pk=pk)
    if request.method == "POST":
        form = AmistadForm(request.POST, instance=amistad)
        if form.is_valid():
            form.save()
            messages.success(request, "Amistad actualizada")
            return redirect("juego:amistad_list")
    else:
        form = AmistadForm(instance=amistad)
    return render(request, "juego/amistades/form.html", {"form": form})


@login_required
def amistad_delete(request, pk):
    amistad = get_object_or_404(Amistad, pk=pk)
    amistad.delete()
    messages.success(request, "Amistad eliminada")
    return redirect("juego:amistad_list")


@login_required
def amistad_detail(request, pk):
    amistad = get_object_or_404(Amistad, pk=pk)
    return render(request, "juego/amistades/detail.html", {"amistad": amistad})


@login_required
def aceptar_amistad(request, pk):
    amistad = get_object_or_404(Amistad, pk=pk)
    amistad.estado = "aceptada"
    amistad.save()
    messages.success(request, "Amistad aceptada")
    return redirect("juego:amistad_list")


@login_required
def rechazar_amistad(request, pk):
    amistad = get_object_or_404(Amistad, pk=pk)
    amistad.estado = "rechazada"
    amistad.save()
    messages.success(request, "Amistad rechazada")
    return redirect("juego:amistad_list")


# ==============================
#   CRUD: REGALOS
# ==============================
@login_required
def regalo_list(request):
    regalos = Regalo.objects.all()
    return render(request, "juego/regalos/list.html", {"regalos": regalos})


@login_required
def regalo_create(request):
    if request.method == "POST":
        form = RegaloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Regalo creado")
            return redirect("juego:regalo_list")
    else:
        form = RegaloForm()
    return render(request, "juego/regalos/form.html", {"form": form})


@login_required
def regalo_update(request, pk):
    regalo = get_object_or_404(Regalo, pk=pk)
    if request.method == "POST":
        form = RegaloForm(request.POST, instance=regalo)
        if form.is_valid():
            form.save()
            messages.success(request, "Regalo actualizado")
            return redirect("juego:regalo_list")
    else:
        form = RegaloForm(instance=regalo)
    return render(request, "juego/regalos/form.html", {"form": form})


@login_required
def regalo_delete(request, pk):
    regalo = get_object_or_404(Regalo, pk=pk)
    regalo.delete()
    messages.success(request, "Regalo eliminado")
    return redirect("juego:regalo_list")


@login_required
def regalo_detail(request, pk):
    regalo = get_object_or_404(Regalo, pk=pk)
    return render(request, "juego/regalos/detail.html", {"regalo": regalo})


@login_required
def enviar_regalo(request, usuario_id):
    if request.method == "POST":
        form = RegaloEnviadoForm(request.POST)
        if form.is_valid():
            regalo = form.save(commit=False)
            regalo.de_usuario = request.user
            regalo.para_usuario_id = usuario_id
            regalo.save()
            messages.success(request, "Regalo enviado")
            return redirect("juego:regalo_list")
    else:
        form = RegaloEnviadoForm()
    return render(request, "juego/regalos/enviar.html", {"form": form})


# ==============================
#   CRUD: SALONES
# ==============================
@login_required
def salon_list(request):
    salones = SalonAmigos.objects.all()
    return render(request, "juego/salones/list.html", {"salones": salones})


@login_required
def salon_create(request):
    if request.method == "POST":
        form = SalonAmigosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salón creado")
            return redirect("juego:salon_list")
    else:
        form = SalonAmigosForm()
    return render(request, "juego/salones/form.html", {"form": form})


@login_required
def salon_update(request, pk):
    salon = get_object_or_404(SalonAmigos, pk=pk)
    if request.method == "POST":
        form = SalonAmigosForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Salón actualizado")
            return redirect("juego:salon_list")
    else:
        form = SalonAmigosForm(instance=salon)
    return render(request, "juego/salones/form.html", {"form": form})


@login_required
def salon_delete(request, pk):
    salon = get_object_or_404(SalonAmigos, pk=pk)
    salon.delete()
    messages.success(request, "Salón eliminado")
    return redirect("juego:salon_list")


@login_required
def salon_detail(request, pk):
    salon = get_object_or_404(SalonAmigos, pk=pk)
    cuartos = CuartoSalon.objects.filter(salon=salon)
    articulos = SalonArticulo.objects.filter(salon=salon)
    return render(request, "juego/salones/detail.html", {"salon": salon, "cuartos": cuartos, "articulos": articulos})


# ==============================
#   RANKINGS Y ESTADÍSTICAS
# ==============================
@login_required
def ranking_territorios(request):
    ranking = Territorio.objects.order_by("-puntos")[:10]
    return render(request, "juego/rankings/territorios.html", {"ranking": ranking})


@login_required
def ranking_salones(request):
    ranking = SalonAmigos.objects.annotate(num_articulos=Count("articulos")).order_by("-num_articulos")[:10]
    return render(request, "juego/rankings/salones.html", {"ranking": ranking})


@login_required
def estadisticas_generales(request):
    total_usuarios = Usuario.objects.count()
    total_lugares = Lugar.objects.count()
    total_misiones = Mision.objects.count()
    total_territorios = Territorio.objects.count()
    total_regalos = Regalo.objects.count()

    return render(request, "juego/estadisticas.html", {
        "total_usuarios": total_usuarios,
        "total_lugares": total_lugares,
        "total_misiones": total_misiones,
        "total_territorios": total_territorios,
        "total_regalos": total_regalos,
    })

