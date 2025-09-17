import secrets
from django.utils.deprecation import MiddlewareMixin

class SincronizarLlaveAdminMiddleware(MiddlewareMixin):
    """
    Middleware que asegura que un usuario admin siempre tenga una llave de seguridad.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            usuario = request.user
            if usuario.rol == "admin" and not usuario.llave_seguridad:
                usuario.llave_seguridad = secrets.token_hex(8)
                usuario.save()
