from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Tabla Persona
class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    cedula_persona = models.CharField(max_length=20, unique=True) # Máximo 8 dígitos
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula_persona})"

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


# 2. Tabla Rol
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_rol

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


# 3. Tabla Usuario
class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    
    # Campo para almacenar el código de verificación por correo
    codigo_verificacion = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        rol_nombre = self.rol.nombre_rol if self.rol else "Sin Rol"
        return f"{self.username} - {rol_nombre}"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"