from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from usuarios.views import favicon_view, crear_password_view

urlpatterns = [
    # Ruta raíz (carga las rutas de la app usuarios)
    path('', include('usuarios.urls')),

    # Rutas bajo /usuarios/
    path('usuarios/', include('usuarios.urls')),

    # Rutas del módulo estudiantes y citas
    path('estudiantes/', include('estudiantes.urls')),

    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Servidor de Favicon
    path('favicon.ico', favicon_view, name='favicon'),

    # Ruta para activación/configuración de contraseña inicial
    path('crear-password/<uidb64>/<token>/', crear_password_view, name='crear_password'),

    # Rutas automáticas para recuperación de contraseña
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset.html',
            email_template_name='usuarios/password_reset_email.html',
            subject_template_name='usuarios/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_sent.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_form.html'
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_done_complete.html'
        ),
        name='password_reset_complete',
    ),
    
]