from django.db import models
from django.contrib.auth.models import AbstractUser


# ------------------------
# USUARIOS
# ------------------------
class Usuario(AbstractUser):
    correo = models.EmailField(unique=True)
    rol = models.CharField(
        max_length=20,
        choices=[("admin", "Administrador"), ("jugador", "Jugador")],
        default="jugador"
    )
    
    # NUEVOS CAMPOS
    admin_token = models.CharField(max_length=100, blank=True, null=True)
    llave_seguridad = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username



# ------------------------
# AMISTADES
# ------------------------
class Amistad(models.Model):
    remitente = models.ForeignKey(
        Usuario, related_name="amistades_enviadas", on_delete=models.CASCADE
    )
    destinatario = models.ForeignKey(
        Usuario, related_name="amistades_recibidas", on_delete=models.CASCADE
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ("pendiente", "Pendiente"),
            ("aceptada", "Aceptada"),
            ("rechazada", "Rechazada"),
        ],
        default="pendiente"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("remitente", "destinatario")

    def __str__(self):
        return f"{self.remitente.username} → {self.destinatario.username} ({self.estado})"


# ------------------------
# LUGARES
# ------------------------
class Lugar(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="lugares/", blank=True, null=True)

    def __str__(self):
        return self.nombre


# ------------------------
# MISIONES
# ------------------------
class Mision(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    lugar = models.ForeignKey(Lugar, on_delete=models.CASCADE, related_name="misiones")
    minijuego_enlace = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.ImageField(upload_to="misiones/", blank=True, null=True)

    def __str__(self):
        return self.titulo


# ------------------------
# ARTÍCULOS (tienda)
# ------------------------
class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


# ------------------------
# TERRITORIOS
# ------------------------
class Territorio(models.Model):
    propietario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="territorios"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("nada", "Nada"),
            ("poco", "Poco"),
            ("normal", "Normal"),
            ("me_gusta", "Me gusta"),
            ("increible", "Increíble"),
        ],
        default="nada"
    )
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.propietario.username})"


# ------------------------
# VISITAS A TERRITORIOS
# ------------------------
class Visita(models.Model):
    visitante = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="visitas_realizadas"
    )
    territorio = models.ForeignKey(
        Territorio, on_delete=models.CASCADE, related_name="visitas"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    calificacion = models.CharField(
        max_length=20,
        choices=[
            ("nada", "Nada"),
            ("poco", "Poco"),
            ("normal", "Normal"),
            ("me_gusta", "Me gusta"),
            ("increible", "Increíble"),
        ],
        default="normal"
    )

    def __str__(self):
        return f"{self.visitante.username} → {self.territorio.nombre}"


# ------------------------
# REGALOS
# ------------------------
class Regalo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    puntos_bonus = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


# ------------------------
# GESTIÓN DE REGALOS ENTRE JUGADORES
# ------------------------
class RegaloEnviado(models.Model):
    regalo = models.ForeignKey(Regalo, on_delete=models.CASCADE)
    de_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="regalos_enviados"
    )
    para_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="regalos_recibidos"
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.de_usuario.username} → {self.para_usuario.username}: {self.regalo.nombre}"


# ------------------------
# SALÓN DE AMIGOS
# ------------------------
class SalonAmigos(models.Model):
    nombre = models.CharField(max_length=100)
    propietario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="salones"
    )

    def __str__(self):
        return f"Salón: {self.nombre} ({self.propietario.username})"


# ------------------------
# CUARTOS DENTRO DEL SALÓN
# ------------------------
class CuartoSalon(models.Model):
    salon = models.ForeignKey(SalonAmigos, on_delete=models.CASCADE, related_name="cuartos")
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"Cuarto {self.nombre} en {self.salon.nombre}"


# ------------------------
# ARTÍCULOS EN EL SALÓN
# ------------------------
class SalonArticulo(models.Model):
    salon = models.ForeignKey(SalonAmigos, on_delete=models.CASCADE, related_name="articulos")
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.articulo.nombre} en {self.salon.nombre} (x{self.cantidad})"
