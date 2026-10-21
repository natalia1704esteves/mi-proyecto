from django.db import models
from usuarios.models import Persona
from django import forms

# --- 1. CATÁLOGOS TERRITORIALES ---

class Municipio(models.Model):
    id_municipio = models.AutoField(primary_key=True)
    nombre_municipio = models.CharField(max_length=100, verbose_name="Nombre del Municipio")

    class Meta:
        db_table = 'municipio'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'

    def __str__(self):
        return self.nombre_municipio


class Parroquia(models.Model):
    id_parroquia = models.AutoField(primary_key=True)
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        related_name='parroquias',
        db_column='id_municipio'
    )
    nombre_parroquia = models.CharField(max_length=100, verbose_name="Nombre de la Parroquia")

    class Meta:
        db_table = 'parroquia'
        verbose_name = 'Parroquia'
        verbose_name_plural = 'Parroquias'

    def __str__(self):
        return f"{self.nombre_parroquia} ({self.municipio.nombre_municipio})"


# --- 2. CATÁLOGOS EDUCATIVOS ---

class Grado(models.Model):
    id_grado = models.AutoField(primary_key=True)
    num_grado = models.CharField(max_length=2, verbose_name="Grado (1-6)")

    class Meta:
        db_table = 'grado'
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'

    def __str__(self):
        return f"{self.num_grado}° Grado"


class Seccion(models.Model):
    id_seccion = models.AutoField(primary_key=True)
    letra_seccion = models.CharField(max_length=2, verbose_name="Sección (A, B, C...)")

    class Meta:
        db_table = 'seccion'
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return f"Sección {self.letra_seccion}"


class Escuela(models.Model):
    id_escuela = models.AutoField(primary_key=True)
    municipio = models.ForeignKey(
        Municipio, 
        on_delete=models.CASCADE, 
        related_name='escuelas',
        db_column='id_municipio',
        null=True, blank=True
    )
    nombre_escuela = models.CharField(max_length=200, verbose_name="Nombre de la Escuela")

    class Meta:
        db_table = 'escuela'
        verbose_name = 'Escuela'
        verbose_name_plural = 'Escuelas'

    def __str__(self):
        return self.nombre_escuela


class PeriodoAcademico(models.Model):
    id_periodo = models.AutoField(primary_key=True)
    nombre_periodo = models.CharField(max_length=20, verbose_name="Ej: 2025-2026")
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

    class Meta:
        db_table = 'periodos_academicos'
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'

    def __str__(self):
        return self.nombre_periodo


# --- 3. REPRESENTANTE Y ESTUDIANTE ---

class Representante(models.Model):
    id_representante = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, db_column='id_persona')
    parentesco = models.CharField(max_length=30, verbose_name="Parentesco (Madre, Padre, Tutor)")
    parroquia = models.ForeignKey(Parroquia, on_delete=models.RESTRICT, db_column='id_parroquia')
    comunidad = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    nro_casa_edf = models.CharField(max_length=50, verbose_name="Nro Casa / Edificio")

    class Meta:
        db_table = 'representante'
        verbose_name = 'Representante'
        verbose_name_plural = 'Representantes'

    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido} ({self.parentesco})"


class Estudiante(models.Model):
    id_estudiante = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, db_column='id_persona')
    representante = models.ForeignKey(Representante, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')

    class Meta:
        db_table = 'estudiante'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"{self.persona.cedula_persona} - {self.persona.nombre} {self.persona.apellido}"


# --- 4. INSCRIPCIÓN ---

class Inscripcion(models.Model):
    id_inscripcion = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='id_estudiante')
    # Estos campos ahora pueden ser nulos por si el estudiante NO está escolarizado
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.RESTRICT, db_column='id_periodo', null=True, blank=True)
    grado = models.ForeignKey(Grado, on_delete=models.RESTRICT, db_column='id_grado', null=True, blank=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.RESTRICT, db_column='id_seccion', null=True, blank=True)
    escuela = models.ForeignKey(Escuela, on_delete=models.RESTRICT, db_column='id_escuela', null=True, blank=True)
    fecha_inscripcion = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'inscripcion'
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'

    def __str__(self):
        if self.escuela and self.grado:
            return f"{self.estudiante} - {self.grado} {self.seccion} en {self.escuela}"
        return f"{self.estudiante} - No Escolarizado ({self.periodo})"

# --- 5. ÁREA PATOLÓGICA Y DIAGNÓSTICOS ---

class AreaPatologica(models.Model):
    id_area_patologica = models.AutoField(primary_key=True)
    nombre_area = models.CharField(max_length=100, verbose_name="Área (Cognitiva, Lenguaje, etc.)")

    class Meta:
        db_table = 'areas_patologicas'
        verbose_name = 'Área Patológica'
        verbose_name_plural = 'Áreas Patológicas'

    def __str__(self):
        return self.nombre_area


class Patologia(models.Model):
    id_patologia = models.AutoField(primary_key=True)
    area_patologica = models.ForeignKey(AreaPatologica, on_delete=models.CASCADE, db_column='id_area_patologica')
    nombre_patologia = models.CharField(max_length=150)

    class Meta:
        db_table = 'patologia'
        verbose_name = 'Patología'
        verbose_name_plural = 'Patologías'

    def __str__(self):
        return f"{self.nombre_patologia} ({self.area_patologica.nombre_area})"


class EstudiantePatologia(models.Model):
    id_estudiante_patologia = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='id_estudiante')
    patologia = models.ForeignKey(Patologia, on_delete=models.RESTRICT, db_column='id_patologia')
    fecha_diagnostico = models.DateField()

    class Meta:
        db_table = 'estudiante_patologia'
        verbose_name = 'Diagnóstico de Estudiante'
        verbose_name_plural = 'Diagnósticos de Estudiantes'

    def __str__(self):
        return f"{self.estudiante} - {self.patologia.nombre_patologia}"

class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)
    id_inscripcion = models.ForeignKey('Inscripcion', on_delete=models.CASCADE, db_column='id_inscripcion')
    fecha_cita = models.DateField()
    hora = models.TimeField()
    estado_cita = models.CharField(max_length=50)
    motivo_cita = models.TextField()

    class Meta:
        db_table = 'cita'

    def __str__(self):
        return f"Cita #{self.id_cita} - {self.fecha_cita}"



 

# --- BITÁCORA / INFORMES ---


class Bitacora(models.Model):
    TIPO_INFORME_CHOICES = [
        ('integral', 'Informe Psicopedagógico Integral'),
        ('especial', 'Informe Psicopedagógico Especial'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, verbose_name="Estudiante")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name="Persona")
    representante = models.ForeignKey(Representante, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Representante")
    
    # AGREGAR ESTA LÍNEA PARA CONECTAR LA PATOLOGÍA DIRECTAMENTE AL INFORME:
    patologia = models.ForeignKey(Patologia, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Patología / Diagnóstico")
    
    cita = models.ForeignKey('Cita', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cita Relacionada")
    
    tipo_informe = models.CharField(
        max_length=50, 
        choices=TIPO_INFORME_CHOICES, 
        default='integral',
        verbose_name="Tipo de Informe"
    )
    fecha_informe = models.DateField(null=True, blank=True, verbose_name="Fecha del Informe")
    edad = models.CharField(max_length=10, null=True, blank=True, verbose_name="Edad")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    motivo_consulta = models.TextField(blank=True, null=True, verbose_name="Motivo de Consulta")
    observaciones_generales = models.TextField(blank=True, null=True, verbose_name="Observaciones / Redacción del Informe")
    recomendaciones = models.TextField(blank=True, null=True, verbose_name="Recomendaciones")
    estado = models.CharField(max_length=20, default='Guardado', verbose_name="Estado")

    class Meta:
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"
        ordering = ['-fecha_creacion']
        db_table = 'bitacora'

    def __str__(self):
        return f"Informe ({self.get_tipo_informe_display()}) - {self.estudiante}"


# --- ARCHIVOS MULTIMEDIA ---

class ExpedienteMultimedia(models.Model):
    TIPO_ARCHIVO_CHOICES = [
        ('informe', 'Informe Psicopedagógico'),
        ('foto', 'Fotografía'),
        ('medico', 'Registro Médico / Salud'),
        ('otro', 'Otro Documento'),
    ]

    id_multimedia = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='expedientes_multimedia')
    bitacora = models.ForeignKey(Bitacora, on_delete=models.SET_NULL, null=True, blank=True, related_name='archivos_adjuntos')
    
    nombre_archivo = models.CharField(max_length=200)
    tipo_archivo = models.CharField(max_length=50, choices=TIPO_ARCHIVO_CHOICES, default='informe')
    archivo = models.FileField(upload_to='expedientes_multimedia/')
    fecha_carga_archivo = models.DateField(auto_now_add=True)
    url_archivo = models.CharField(max_length=500, blank=True, null=True)
    perfil_general_diagnostico = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_archivo} - {self.estudiante}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.url_archivo:
            self.url_archivo = self.archivo.url
            super().save(update_fields=['url_archivo'])