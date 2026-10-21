from django.contrib import admin
from .models import (
    Municipio, Parroquia, Grado, Seccion, Escuela, PeriodoAcademico,
    Representante, Estudiante, Inscripcion, AreaPatologica, Patologia, EstudiantePatologia
)

admin.site.register(Municipio)
admin.site.register(Parroquia)
admin.site.register(Grado)
admin.site.register(Seccion)
admin.site.register(Escuela)
admin.site.register(PeriodoAcademico)
admin.site.register(Representante)
admin.site.register(Estudiante)
admin.site.register(Inscripcion)
admin.site.register(AreaPatologica)
admin.site.register(Patologia)
admin.site.register(EstudiantePatologia)