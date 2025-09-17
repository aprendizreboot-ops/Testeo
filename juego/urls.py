from django.urls import path
from . import views

app_name = "juego"

urlpatterns = [
    # =========================
    # Autenticación
    # =========================
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("", views.home, name="home"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # =========================
    # Usuarios (solo admin)
    # =========================
    path("usuarios/", views.usuario_list, name="usuario_list"),
    path("usuarios/create/", views.usuario_create, name="usuario_create"),
    path("usuarios/<int:pk>/edit/", views.usuario_update, name="usuario_update"),
    path("usuarios/<int:pk>/delete/", views.usuario_delete, name="usuario_delete"),
    path("usuarios/<int:pk>/", views.usuario_detail, name="usuario_detail"),

    # =========================
    # Lugares
    # =========================
    path("lugares/", views.lugar_list, name="lugar_list"),
    path("lugares/create/", views.lugar_create, name="lugar_create"),
    path("lugares/<int:pk>/edit/", views.lugar_update, name="lugar_update"),
    path("lugares/<int:pk>/delete/", views.lugar_delete, name="lugar_delete"),
    path("lugares/<int:pk>/", views.lugar_detail, name="lugar_detail"),

    # =========================
    # Misiones
    # =========================
    path("misiones/", views.mision_list, name="mision_list"),
    path("misiones/create/", views.mision_create, name="mision_create"),
    path("misiones/<int:pk>/edit/", views.mision_update, name="mision_update"),
    path("misiones/<int:pk>/delete/", views.mision_delete, name="mision_delete"),
    path("misiones/<int:pk>/", views.mision_detail, name="mision_detail"),

    # =========================
    # Artículos
    # =========================
    path("articulos/", views.articulo_list, name="articulo_list"),
    path("articulos/create/", views.articulo_create, name="articulo_create"),
    path("articulos/<int:pk>/edit/", views.articulo_update, name="articulo_update"),
    path("articulos/<int:pk>/delete/", views.articulo_delete, name="articulo_delete"),
    path("articulos/<int:pk>/", views.articulo_detail, name="articulo_detail"),

    # =========================
    # Territorios
    # =========================
    path("territorios/", views.territorio_list, name="territorio_list"),
    path("territorios/create/", views.territorio_create, name="territorio_create"),
    path("territorios/<int:pk>/edit/", views.territorio_update, name="territorio_update"),
    path("territorios/<int:pk>/delete/", views.territorio_delete, name="territorio_delete"),
    path("territorios/<int:pk>/", views.territorio_detail, name="territorio_detail"),
    path("territorios/<int:pk>/visitar/", views.visitar_territorio, name="visitar_territorio"),

    # =========================
    # Amistades
    # =========================
    path("amistades/", views.amistad_list, name="amistad_list"),
    path("amistades/create/", views.amistad_create, name="amistad_create"),
    path("amistades/<int:pk>/edit/", views.amistad_update, name="amistad_update"),
    path("amistades/<int:pk>/delete/", views.amistad_delete, name="amistad_delete"),
    path("amistades/<int:pk>/", views.amistad_detail, name="amistad_detail"),
    path("amistades/<int:pk>/aceptar/", views.aceptar_amistad, name="aceptar_amistad"),
    path("amistades/<int:pk>/rechazar/", views.rechazar_amistad, name="rechazar_amistad"),

    # =========================
    # Regalos
    # =========================
    path("regalos/", views.regalo_list, name="regalo_list"),
    path("regalos/create/", views.regalo_create, name="regalo_create"),
    path("regalos/<int:pk>/edit/", views.regalo_update, name="regalo_update"),
    path("regalos/<int:pk>/delete/", views.regalo_delete, name="regalo_delete"),
    path("regalos/<int:pk>/", views.regalo_detail, name="regalo_detail"),
    path("regalos/enviar/<int:usuario_id>/", views.enviar_regalo, name="enviar_regalo"),

    # =========================
    # Salones
    # =========================
    path("salones/", views.salon_list, name="salon_list"),
    path("salones/create/", views.salon_create, name="salon_create"),
    path("salones/<int:pk>/edit/", views.salon_update, name="salon_update"),
    path("salones/<int:pk>/delete/", views.salon_delete, name="salon_delete"),
    path("salones/<int:pk>/", views.salon_detail, name="salon_detail"),

    # =========================
    # Rankings y estadísticas
    # =========================
    path("rankings/territorios/", views.ranking_territorios, name="ranking_territorios"),
    path("rankings/salones/", views.ranking_salones, name="ranking_salones"),
    path("estadisticas/", views.estadisticas_generales, name="estadisticas_generales"),
]
