from django.contrib import admin
from .models import (Usuario, Lugar, Mision, Articulo,
                     Territorio, SalonAmigos, CuartoSalon,
                     SalonArticulo, Regalo, Visita, Amistad)

admin.site.register(Usuario)
admin.site.register(Lugar)
admin.site.register(Mision)
admin.site.register(Articulo)
admin.site.register(Territorio)
admin.site.register(SalonAmigos)
admin.site.register(CuartoSalon)
admin.site.register(SalonArticulo)
admin.site.register(Regalo)
admin.site.register(Visita)
admin.site.register(Amistad)
