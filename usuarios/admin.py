from django.contrib import admin
from .models import Persona, Rol, Usuario

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('cedula_persona', 'nombre', 'apellido', 'fecha_nacimiento', 'sexo')
    search_fields = ('cedula_persona', 'nombre', 'apellido')

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre_rol')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'persona', 'is_staff')
    list_filter = ('rol', 'is_staff')
    search_fields = ('username', 'email')