import os
import re
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse, Http404
from .models import Usuario, Persona, Rol


# Función auxiliar para comprobar si el usuario es Administrador / Superusuario
def es_administrador(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# 1. Vista de Inicio (Página Principal)
@login_required(login_url='login')
def home_view(request):
    return render(request, 'usuarios/home.html')


# 2. Vista de Iniciar Sesión (Login)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')

        # Se intenta autenticar con el nombre de usuario (que es el correo)
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos, o la cuenta no ha sido verificada.")

    return render(request, 'usuarios/login.html')


# 3. Vista de Cerrar Sesión (Logout)
def logout_view(request):
    logout(request)
    return redirect('login')


# 4. Vista de Registro de Usuario (Protegida - Solo Administradores)
@login_required(login_url='login')
@user_passes_test(es_administrador, login_url='home')
def registro_view(request):
    roles = Rol.objects.all()

    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        rol_id = request.POST.get('rol')

        # ----------------------------------------------------
        # 1. Validación de Cédula
        # ----------------------------------------------------
        if not cedula.isdigit():
            messages.error(request, "La cédula solo debe contener números.")
            return render(request, 'usuarios/registro.html', {'roles': roles})

        if len(cedula) == 7:
            cedula = '0' + cedula
        elif len(cedula) != 8:
            messages.error(request, "La cédula debe contener entre 7 u 8 números.")
            return render(request, 'usuarios/registro.html', {'roles': roles})

        # Limpieza de cuenta no verificada previo si existe por Cédula
        persona_existente = Persona.objects.filter(cedula_persona=cedula).first()
        if persona_existente:
            usuario_asociado = Usuario.objects.filter(persona=persona_existente).first()
            if usuario_asociado and not usuario_asociado.is_active:
                usuario_asociado.delete()
                persona_existente.delete()
            elif usuario_asociado and usuario_asociado.is_active:
                messages.error(request, "Esta cédula ya se encuentra registrada y activa.")
                return render(request, 'usuarios/registro.html', {'roles': roles})

        # ----------------------------------------------------
        # 2. Validación de Correo / Username
        # ----------------------------------------------------
        usuario_email = Usuario.objects.filter(email=email).first()
        if usuario_email:
            if not usuario_email.is_active:
                persona_asociada = usuario_email.persona
                usuario_email.delete()
                if persona_asociada:
                    persona_asociada.delete()
            else:
                messages.error(request, "El correo electrónico ya está registrado.")
                return render(request, 'usuarios/registro.html', {'roles': roles})

        # ----------------------------------------------------
        # 3. Validación de Rol Seleccionado
        # ----------------------------------------------------
        if not rol_id:
            messages.error(request, "Debe seleccionar un rol para el usuario.")
            return render(request, 'usuarios/registro.html', {'roles': roles})

        try:
            rol_obj = Rol.objects.get(pk=rol_id)
        except (Rol.DoesNotExist, ValueError):
            messages.error(request, "El rol seleccionado no es válido.")
            return render(request, 'usuarios/registro.html', {'roles': roles})

        # ----------------------------------------------------
        # 4. Crear Persona y Usuario (Inactivo)
        # ----------------------------------------------------
        persona = Persona.objects.create(
            cedula_persona=cedula,
            nombre=nombre,
            apellido=apellido
        )

        es_staff_flag = False
        if "psicopedagogo" in rol_obj.nombre_rol.lower() or "director" in rol_obj.nombre_rol.lower():
            es_staff_flag = True

        usuario = Usuario.objects.create_user(
            username=email,
            email=email,
            persona=persona,
            rol=rol_obj,
            is_active=False,
            is_staff=es_staff_flag
        )
        usuario.set_unusable_password()
        usuario.save()

        # ----------------------------------------------------
        # 5. Generación de Link Seguro y Envío de Correo
        # ----------------------------------------------------
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)
        activation_link = f"http://{request.get_host()}/crear-password/{uid}/{token}/"

        asunto = "Bienvenido a SIGEP - Configuración de tu cuenta"
        mensaje = (
            f"Hola {nombre} {apellido},\n\n"
            f"Se ha registrado tu cuenta en el sistema SIGEP con el rol de {rol_obj.nombre_rol}.\n"
            f"Para activar tu cuenta y configurar tu contraseña de acceso, por favor ingresa al siguiente enlace:\n\n"
            f"{activation_link}\n\n"
            f"Este enlace es de uso personal y único."
        )

        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, f"Usuario {nombre} {apellido} registrado exitosamente. Se ha enviado una invitación a su correo electrónico.")
        except Exception as e:
            messages.error(request, f"Usuario registrado pero hubo un fallo al enviar el correo: {e}")

        return redirect('configuracion')

    return render(request, 'usuarios/registro.html', {'roles': roles})


# 5. Vista para Configurar Contraseña mediante Enlace Seguro
def crear_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')

            # Validaciones de Contraseña
            if password != password_confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, 'usuarios/crear_password.html')

            if len(password) < 8 or len(password) > 15:
                messages.error(request, "La contraseña debe tener entre 8 y 15 caracteres.")
                return render(request, 'usuarios/crear_password.html')

            if not re.search(r'[A-Z]', password):
                messages.error(request, "La contraseña debe contener al menos una letra mayúscula.")
                return render(request, 'usuarios/crear_password.html')

            if not re.search(r'\d', password):
                messages.error(request, "La contraseña debe contener al menos un número.")
                return render(request, 'usuarios/crear_password.html')

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                messages.error(request, "La contraseña debe contener al menos un carácter especial.")
                return render(request, 'usuarios/crear_password.html')

            # Asignación de contraseña y activación
            usuario.set_password(password)
            usuario.is_active = True
            usuario.save()

            # MEDIDA DE SEGURIDAD: Cierre de cualquier sesión activa antes de redirigir
            logout(request)

            messages.success(request, "¡Contraseña establecida con éxito! Por favor, inicia sesión con tus credenciales.")
            return redirect('login')

        return render(request, 'usuarios/crear_password.html')
    else:
        messages.error(request, "El enlace de configuración es inválido o ha expirado.")
        return redirect('login')


def password_reset_confirm_view(request, uidb64=None, token=None):
    return render(request, 'usuarios/password_reset_form.html')


# 6. Vista Servidora de Favicon
def favicon_view(request):
    icon_path = os.path.join(settings.BASE_DIR, 'usuarios', 'static', 'usuarios', 'imagenes', 'favico.svg')
    
    if os.path.exists(icon_path):
        return FileResponse(open(icon_path, 'rb'), content_type='image/svg+xml')
    else:
        raise Http404("Favicon no encontrado")


# 7. Configuración de Usuario
@login_required
def configuracion_view(request):
    persona = getattr(request.user, 'persona', None)
    roles = Rol.objects.all()

    if request.method == 'POST':
        nuevo_email = request.POST.get('email', '').strip()

        if nuevo_email and nuevo_email != request.user.email:
            if Usuario.objects.filter(email=nuevo_email).exists():
                messages.error(request, "El correo electrónico ya está registrado por otro usuario.")
                return redirect('configuracion')

            codigo = f"{random.randint(100000, 999999)}"
            request.user.codigo_verificacion = codigo
            request.user.save()

            request.session['nuevo_email_pendiente'] = nuevo_email

            asunto = "SIGEP - Código de verificación para cambio de correo"
            mensaje = f"Hola {request.user.first_name},\n\nTu código para confirmar el cambio de correo a {nuevo_email} es: {codigo}"
            
            try:
                send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [nuevo_email], fail_silently=False)
                messages.info(request, f"Se ha enviado un código de verificación a {nuevo_email}.")
                return redirect('verificar_cambio_email')
            except Exception as e:
                messages.error(request, f"Error al enviar el correo de verificación: {e}")
                return redirect('configuracion')

        messages.success(request, "Configuración guardada correctamente.")
        return redirect('configuracion')

    return render(request, 'usuarios/configuracion.html', {
        'persona': persona,
        'roles': roles
    })


@login_required
def verificar_cambio_email_view(request):
    nuevo_email = request.session.get('nuevo_email_pendiente')

    if not nuevo_email:
        return redirect('configuracion')

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()

        if codigo_ingresado == request.user.codigo_verificacion:
            user = request.user
            user.email = nuevo_email
            user.username = nuevo_email
            user.codigo_verificacion = None
            user.save()

            del request.session['nuevo_email_pendiente']

            messages.success(request, "Correo electrónico actualizado con éxito.")
            return redirect('configuracion')
        else:
            messages.error(request, "El código ingresado es incorrecto.")

    return render(request, 'usuarios/verificar_codigo_email.html', {'nuevo_email': nuevo_email})