from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import (
    Cita, Bitacora, Estudiante, ExpedienteMultimedia,
    Patologia, AreaPatologica, Municipio, Parroquia,
    Grado, Seccion, Escuela, PeriodoAcademico, Representante, Inscripcion
)
from .forms import CitaForm
from usuarios.models import Persona


@login_required(login_url='login')
def registrar_estudiante_view(request):
    municipios = Municipio.objects.all().order_by('nombre_municipio')
    parroquias = Parroquia.objects.all().order_by('nombre_parroquia')
    grados = Grado.objects.all().order_by('num_grado')
    secciones = Seccion.objects.all().order_by('letra_seccion')
    escuelas = Escuela.objects.all().order_by('nombre_escuela')
    periodos = PeriodoAcademico.objects.all().order_by('-fecha_inicio')

    if request.method == 'POST':
        rep_cedula = request.POST.get('rep_cedula', '').strip()
        rep_nombre = request.POST.get('rep_nombre', '').strip()
        rep_apellido = request.POST.get('rep_apellido', '').strip()
        rep_parentesco = request.POST.get('rep_parentesco', '').strip()
        rep_parroquia_id = request.POST.get('rep_parroquia')
        rep_sector = request.POST.get('rep_sector', '').strip()
        rep_calle = request.POST.get('rep_calle', '').strip()
        rep_casa = request.POST.get('rep_casa', '').strip()

        est_cedula = request.POST.get('est_cedula', '').strip()
        est_nombre = request.POST.get('est_nombre', '').strip()
        est_apellido = request.POST.get('est_apellido', '').strip()
        est_fecha_nac = request.POST.get('est_fecha_nac')
        est_sexo = request.POST.get('est_sexo')

        periodo_id = request.POST.get('periodo')
        grado_id = request.POST.get('grado')
        seccion_id = request.POST.get('seccion')
        escuela_id = request.POST.get('escuela')

        if not est_cedula or not est_nombre or not est_apellido:
            messages.error(request, "Por favor completa todos los campos obligatorios del estudiante.")
            return redirect('estudiantes:registrar_estudiante')

        try:
            with transaction.atomic():
                persona_rep, _ = Persona.objects.get_or_create(
                    cedula_persona=rep_cedula,
                    defaults={'nombre': rep_nombre, 'apellido': rep_apellido}
                )

                parroquia_obj = Parroquia.objects.get(pk=rep_parroquia_id) if rep_parroquia_id else None
                representante_obj, _ = Representante.objects.get_or_create(
                    persona=persona_rep,
                    defaults={
                        'parentesco': rep_parentesco,
                        'parroquia': parroquia_obj,
                        'sector': rep_sector,
                        'calle': rep_calle,
                        'nro_casa_edf': rep_casa
                    }
                )

                persona_est = Persona.objects.create(
                    cedula_persona=est_cedula,
                    nombre=est_nombre,
                    apellido=est_apellido,
                    fecha_nacimiento=est_fecha_nac if est_fecha_nac else None,
                    sexo=est_sexo
                )

                estudiante_obj = Estudiante.objects.create(
                    persona=persona_est,
                    representante=representante_obj
                )

                if periodo_id and grado_id and seccion_id and escuela_id:
                    Inscripcion.objects.create(
                        estudiante=estudiante_obj,
                        periodo_id=periodo_id,
                        grado_id=grado_id,
                        seccion_id=seccion_id,
                        escuela_id=escuela_id
                    )

                messages.success(request, f"Estudiante {est_nombre} {est_apellido} registrado con éxito.")
                return redirect('estudiantes:registrar_estudiante')

        except Exception as e:
            messages.error(request, f"Ocurrió un error al registrar: {str(e)}")
            return redirect('estudiantes:registrar_estudiante')

    context = {
        'municipios': municipios,
        'parroquias': parroquias,
        'grados': grados,
        'secciones': secciones,
        'escuelas': escuelas,
        'periodos': periodos,
    }
    return render(request, 'estudiantes/registrar_estudiante.html', context)


@login_required(login_url='login')
def listar_estudiantes_view(request):
    estudiantes = Estudiante.objects.all().select_related('persona', 'representante__persona')
    context = {'estudiantes': estudiantes}
    return render(request, 'estudiantes/listar_estudiantes.html', context)


@login_required(login_url='login')
def editar_estudiante_view(request, pk):
    estudiante = Estudiante.objects.get(id_estudiante=pk)
    persona_est = estudiante.persona
    representante = estudiante.representante
    persona_rep = representante.persona if representante else None
    
    municipios = Municipio.objects.all().order_by('nombre_municipio')
    parroquias = Parroquia.objects.all().order_by('nombre_parroquia')
    grados = Grado.objects.all().order_by('num_grado')
    secciones = Seccion.objects.all().order_by('letra_seccion')
    escuelas = Escuela.objects.all().order_by('nombre_escuela')
    periodos = PeriodoAcademico.objects.all().order_by('-fecha_inicio')
    
    inscripcion_actual = Inscripcion.objects.filter(estudiante=estudiante).first()

    if request.method == 'POST':
        rep_cedula = request.POST.get('rep_cedula', '').strip()
        rep_nombre = request.POST.get('rep_nombre', '').strip()
        rep_apellido = request.POST.get('rep_apellido', '').strip()
        rep_parentesco = request.POST.get('rep_parentesco', '').strip()
        rep_parroquia_id = request.POST.get('rep_parroquia')
        rep_sector = request.POST.get('rep_sector', '').strip()
        rep_calle = request.POST.get('rep_calle', '').strip()
        rep_casa = request.POST.get('rep_casa', '').strip()

        est_cedula = request.POST.get('est_cedula', '').strip()
        est_nombre = request.POST.get('est_nombre', '').strip()
        est_apellido = request.POST.get('est_apellido', '').strip()
        est_fecha_nac = request.POST.get('est_fecha_nac')
        est_sexo = request.POST.get('est_sexo')

        condicion = request.POST.get('condicion_escolaridad')
        periodo_id = request.POST.get('periodo')
        grado_id = request.POST.get('grado')
        seccion_id = request.POST.get('seccion')
        escuela_id = request.POST.get('escuela')

        try:
            with transaction.atomic():
                if persona_rep:
                    persona_rep.cedula_persona = rep_cedula
                    persona_rep.nombre = rep_nombre
                    persona_rep.apellido = rep_apellido
                    persona_rep.save()
                
                if representante:
                    representante.parentesco = rep_parentesco
                    representante.parroquia_id = rep_parroquia_id if rep_parroquia_id else None
                    representante.sector = rep_sector
                    representante.calle = rep_calle
                    representante.nro_casa_edf = rep_casa
                    representante.save()

                persona_est.cedula_persona = est_cedula
                persona_est.nombre = est_nombre
                persona_est.apellido = est_apellido
                persona_est.fecha_nacimiento = est_fecha_nac if est_fecha_nac else None
                persona_est.sexo = est_sexo
                persona_est.save()

                if condicion == 'escolarizado':
                    if inscripcion_actual:
                        inscripcion_actual.periodo_id = periodo_id if periodo_id else None
                        inscripcion_actual.grado_id = grado_id if grado_id else None
                        inscripcion_actual.seccion_id = seccion_id if seccion_id else None
                        inscripcion_actual.escuela_id = escuela_id if escuela_id else None
                        inscripcion_actual.save()
                    else:
                        Inscripcion.objects.create(
                            estudiante=estudiante,
                            periodo_id=periodo_id if periodo_id else None,
                            grado_id=grado_id if grado_id else None,
                            seccion_id=seccion_id if seccion_id else None,
                            escuela_id=escuela_id if escuela_id else None
                        )
                else:
                    if inscripcion_actual:
                        inscripcion_actual.delete()

                messages.success(request, f"Estudiante {est_nombre} actualizado con éxito.")
                return redirect('estudiantes:listar_estudiantes')

        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")

    context = {
        'estudiante': estudiante,
        'persona_est': persona_est,
        'representante': representante,
        'persona_rep': persona_rep,
        'inscripcion_actual': inscripcion_actual,
        'municipios': municipios,
        'parroquias': parroquias,
        'grados': grados,
        'secciones': secciones,
        'escuelas': escuelas,
        'periodos': periodos,
    }
    return render(request, 'estudiantes/editar_estudiante.html', context)


@login_required(login_url='login')
def eliminar_estudiante_view(request, pk):
    try:
        estudiante = Estudiante.objects.get(id_estudiante=pk)
        persona = estudiante.persona
        estudiante.delete()
        if persona:
            persona.delete()
        messages.success(request, "Estudiante eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar el registro: {str(e)}")
    return redirect('estudiantes:listar_estudiantes')


# --- MÓDULO DE CITAS ---

@login_required(login_url='login')
def registrar_cita(request):
    query = request.GET.get('q', '').strip()
    estudiantes = []
    
    if query:
        estudiantes = Estudiante.objects.filter(
            Q(persona__nombre__icontains=query) |
            Q(persona__apellido__icontains=query) |
            Q(persona__cedula_persona__icontains=query)
        ).select_related('persona').distinct()

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita registrada con éxito.")
            return redirect('estudiantes:listar_citas')
    else:
        form = CitaForm()

    context = {
        'form': form,
        'estudiantes': estudiantes,
        'query': query,
    }
    return render(request, 'estudiantes/registrar_cita.html', context)


@login_required(login_url='login')
def listar_citas(request):
    citas = Cita.objects.all().select_related('id_inscripcion__estudiante__persona')
    context = {'citas': citas}
    return render(request, 'estudiantes/listar_citas.html', context)


@login_required(login_url='login')
def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada con éxito.")
            return redirect('estudiantes:listar_citas')
    else:
        form = CitaForm(instance=cita)

    context = {
        'form': form,
        'cita': cita,
    }
    return render(request, 'estudiantes/registrar_cita.html', context)


@login_required(login_url='login')
def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    cita.delete()
    messages.success(request, "Cita eliminada con éxito.")
    return redirect('estudiantes:listar_citas')


# --- MÓDULO DE BITÁCORA / INFORMES (UNIFICADO) ---

@login_required(login_url='login')
def listar_bitacoras(request):
    query = request.GET.get('q', '').strip()
    bitacoras = Bitacora.objects.all().order_by('-fecha_creacion')

    if query:
        bitacoras = bitacoras.filter(
            Q(estudiante__persona__nombre__icontains=query) |
            Q(estudiante__persona__apellido__icontains=query) |
            Q(estudiante__persona__cedula_persona__icontains=query)
        )

    context = {
        'bitacoras': bitacoras,
        'query': query,
    }
    return render(request, 'estudiantes/listar_bitacoras.html', context)


@login_required(login_url='login')
def buscar_estudiante_bitacora(request):
    tipo_informe = request.GET.get('tipo', 'integral')
    query = request.GET.get('q', '').strip()
    
    estudiantes = Estudiante.objects.select_related('persona', 'representante__persona').all()
    
    if query:
        estudiantes = estudiantes.filter(
            Q(persona__nombre__icontains=query) |
            Q(persona__apellido__icontains=query) |
            Q(persona__cedula_persona__icontains=query)
        ).distinct()
    
    context = {
        'tipo_informe': tipo_informe,
        'estudiantes': estudiantes,
        'query': query,
    }
    return render(request, 'estudiantes/buscar_estudiante_bitacora.html', context)


@login_required(login_url='login')
def redactar_informe_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id_estudiante=estudiante_id)
    tipo_solicitado = request.GET.get('tipo', 'integral')
    
    tipos_validos = ['integral', 'especial']
    if hasattr(Bitacora, 'TIPO_INFORME_CHOICES'):
        tipos_validos = [choice[0] for choice in Bitacora.TIPO_INFORME_CHOICES]
        
    tipo_informe = tipo_solicitado if tipo_solicitado in tipos_validos else 'integral'
    
    if request.method == 'POST':
        fecha_ingresada = request.POST.get('fecha_informe') or request.POST.get('fecha')
        patologia_id = request.POST.get('patologia')
        patologia_obj = Patologia.objects.filter(pk=patologia_id).first() if patologia_id else None

        kwargs_bitacora = {
            'estudiante': estudiante,
            'persona': estudiante.persona,
            'representante': estudiante.representante,
            'tipo_informe': tipo_informe,
            'fecha_informe': fecha_ingresada if fecha_ingresada else None,
            'patologia': patologia_obj,
            'edad': request.POST.get('edad', ''),
            'motivo_consulta': request.POST.get('motivo_consulta', ''),
            'observaciones_generales': request.POST.get('observaciones_generales') or request.POST.get('observaciones', ''),
            'recomendaciones': request.POST.get('recomendaciones', ''),
            'estado': 'Guardado'
        }

        Bitacora.objects.create(**kwargs_bitacora)
        messages.success(request, "¡Informe guardado exitosamente!")
        return redirect('estudiantes:listar_bitacoras')

    patologias = Patologia.objects.all().order_by('nombre_patologia')
    areas_patologicas = AreaPatologica.objects.all().order_by('nombre_area')

    context = {
        'estudiante': estudiante,
        'tipo_informe': tipo_informe,
        'patologias': patologias,
        'areas_patologicas': areas_patologicas,
        'solo_lectura': False,
        'editando': False,
    }

    if tipo_informe == 'especial':
        return render(request, 'estudiantes/informe_especial_form.html', context)
    
    return render(request, 'estudiantes/plantilla.html', context)


@login_required(login_url='login')
def ver_bitacora(request, bitacora_id):
    bitacora = get_object_or_404(Bitacora, id=bitacora_id)
    estudiante = bitacora.estudiante
    tipo_informe = getattr(bitacora, 'tipo_informe', 'integral')
    
    patologias = Patologia.objects.all().order_by('nombre_patologia')
    areas_patologicas = AreaPatologica.objects.all().order_by('nombre_area')

    context = {
        'bitacora': bitacora,
        'estudiante': estudiante,
        'solo_lectura': True,
        'editando': False,
        'tipo_informe': tipo_informe,
        'patologias': patologias,
        'areas_patologicas': areas_patologicas,
    }

    if tipo_informe == 'especial':
        return render(request, 'estudiantes/informe_especial_form.html', context)
    
    return render(request, 'estudiantes/plantilla.html', context)


@login_required(login_url='login')
def editar_bitacora(request, bitacora_id):
    bitacora = get_object_or_404(Bitacora, id=bitacora_id)
    estudiante = bitacora.estudiante
    tipo_informe = getattr(bitacora, 'tipo_informe', 'integral')
    
    if request.method == 'POST':
        bitacora.edad = request.POST.get('edad', bitacora.edad)
        
        fecha_input = request.POST.get('fecha_informe') or request.POST.get('fecha')
        if fecha_input:
            bitacora.fecha_informe = fecha_input

        patologia_id = request.POST.get('patologia')
        if patologia_id:
            bitacora.patologia = Patologia.objects.filter(pk=patologia_id).first()
        else:
            bitacora.patologia = None

        bitacora.motivo_consulta = request.POST.get('motivo_consulta', bitacora.motivo_consulta)
        
        obs_input = request.POST.get('observaciones_generales') or request.POST.get('observaciones')
        if obs_input is not None:
            bitacora.observaciones_generales = obs_input
                
        bitacora.recomendaciones = request.POST.get('recomendaciones', bitacora.recomendaciones)
            
        bitacora.save()
        messages.success(request, "¡Informe actualizado exitosamente!")
        return redirect('estudiantes:listar_bitacoras')

    patologias = Patologia.objects.all().order_by('nombre_patologia')
    areas_patologicas = AreaPatologica.objects.all().order_by('nombre_area')

    context = {
        'bitacora': bitacora,
        'estudiante': estudiante,
        'editando': True,
        'solo_lectura': False,
        'tipo_informe': tipo_informe,
        'patologias': patologias,
        'areas_patologicas': areas_patologicas,
    }

    if tipo_informe == 'especial':
        return render(request, 'estudiantes/informe_especial_form.html', context)

    return render(request, 'estudiantes/plantilla.html', context)


@login_required(login_url='login')
def eliminar_bitacora(request, bitacora_id):
    bitacora = get_object_or_404(Bitacora, id=bitacora_id)
    bitacora.delete()
    messages.success(request, "Informe eliminado correctamente.")
    return redirect('estudiantes:listar_bitacoras')


@require_POST
def crear_patologia_ajax(request):
    nombre_patologia = request.POST.get('nombre_patologia', '').strip()
    id_area = request.POST.get('area_patologica')

    if not nombre_patologia:
        return JsonResponse({'success': False, 'error': 'El nombre de la patología es obligatorio.'}, status=400)

    try:
        area = AreaPatologica.objects.get(pk=id_area) if id_area else None
        
        nueva_patologia = Patologia.objects.create(
            nombre_patologia=nombre_patologia,
            area_patologica=area
        )
        
        return JsonResponse({
            'success': True,
            'id': nueva_patologia.id_patologia,
            'nombre': nueva_patologia.nombre_patologia
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# --- MÓDULO EXPEDIENTES MULTIMEDIA ---

@login_required(login_url='login')
def modulo_expedientes_multimedia(request):
    query = request.GET.get('q', '')
    informes_disponibles = Bitacora.objects.select_related('estudiante__persona').order_by('-fecha_creacion')

    estudiantes_con_expediente = Estudiante.objects.filter(
        expedientes_multimedia__isnull=False
    ).distinct()

    if query:
        estudiantes_con_expediente = estudiantes_con_expediente.filter(
            Q(persona__nombre__icontains=query) | Q(persona__cedula_persona__icontains=query)
        )

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear_expediente':
            bitacora_id = request.POST.get('bitacora_id')
            bitacora_obj = get_object_or_404(Bitacora, pk=bitacora_id)
            est_obj = bitacora_obj.estudiante

            if not ExpedienteMultimedia.objects.filter(estudiante=est_obj, bitacora=bitacora_obj).exists():
                ExpedienteMultimedia.objects.create(
                    estudiante=est_obj,
                    bitacora=bitacora_obj,
                    nombre_archivo=f"Informe - {bitacora_obj.get_tipo_informe_display()}",
                    tipo_archivo='informe',
                    perfil_general_diagnostico="Informe psicopedagógico oficial del estudiante."
                )
                messages.success(request, f"¡Carpeta e informe vinculado correctamente para {est_obj.persona.nombre}!")
            else:
                messages.warning(request, "Este informe ya se encuentra registrado en la carpeta del estudiante.")
            return redirect('estudiantes:detalle_expediente_estudiante', estudiante_id=est_obj.pk)

        elif accion == 'eliminar_carpeta':
            est_id = request.POST.get('estudiante_id')
            est_obj = get_object_or_404(Estudiante, pk=est_id)
            ExpedienteMultimedia.objects.filter(estudiante=est_obj).delete()
            messages.success(request, f"¡Carpeta de {est_obj.persona.nombre} eliminada correctamente!")
            return redirect('estudiantes:expediente_multimedia')

    context = {
        'informes_disponibles': informes_disponibles,
        'estudiantes': estudiantes_con_expediente,
        'query': query,
    }
    return render(request, 'estudiantes/expediente_multimedia.html', context)


@login_required(login_url='login')
def detalle_expediente_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    archivos = ExpedienteMultimedia.objects.filter(estudiante=estudiante).select_related('bitacora').order_by('-fecha_carga_archivo')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'subir_medico':
            nombre_doc = request.POST.get('nombre_archivo')
            archivo_subido = request.FILES.get('archivo')
            observaciones = request.POST.get('perfil_general_diagnostico')

            if archivo_subido:
                ExpedienteMultimedia.objects.create(
                    estudiante=estudiante,
                    nombre_archivo=nombre_doc,
                    tipo_archivo='medico',
                    archivo=archivo_subido,
                    perfil_general_diagnostico=observaciones
                )
                messages.success(request, "¡Expediente médico / foto adjuntada correctamente!")
            return redirect('estudiantes:detalle_expediente_estudiante', estudiante_id=estudiante.pk)

        elif accion == 'editar_archivo':
            file_id = request.POST.get('archivo_id')
            doc_obj = get_object_or_404(ExpedienteMultimedia, pk=file_id)
            doc_obj.nombre_archivo = request.POST.get('nombre_archivo')
            doc_obj.perfil_general_diagnostico = request.POST.get('perfil_general_diagnostico')
            if request.FILES.get('archivo'):
                doc_obj.archivo = request.FILES.get('archivo')
            doc_obj.save()
            messages.success(request, "¡Documento actualizado!")
            return redirect('estudiantes:detalle_expediente_estudiante', estudiante_id=estudiante.pk)

        elif accion == 'eliminar_archivo':
            file_id = request.POST.get('archivo_id')
            doc_obj = get_object_or_404(ExpedienteMultimedia, pk=file_id)
            doc_obj.delete()
            messages.success(request, "¡Documento eliminado del expediente!")
            return redirect('estudiantes:detalle_expediente_estudiante', estudiante_id=estudiante.pk)

    context = {
        'estudiante': estudiante,
        'archivos': archivos,
    }
    return render(request, 'estudiantes/detalle_expediente.html', context)


# --- MÓDULO DE REPORTES E INDICADORES ---

@login_required(login_url='login')
def modulo_reportes(request):
    hoy = timezone.now().date()
    
    try:
        mes = int(request.GET.get('mes', hoy.month))
    except (ValueError, TypeError):
        mes = hoy.month

    try:
        anio = int(request.GET.get('anio', hoy.year))
    except (ValueError, TypeError):
        anio = hoy.year

    estado_filtro = request.GET.get('estado', '').strip()
    sexo_filtro = request.GET.get('sexo', '').strip()

    citas_mes = Cita.objects.filter(fecha_cita__year=anio, fecha_cita__month=mes)
    
    if sexo_filtro:
        citas_mes = citas_mes.filter(
            Q(id_inscripcion__estudiante__persona__sexo__iexact=sexo_filtro) |
            Q(id_inscripcion__estudiante__persona__sexo__istartswith=sexo_filtro[0])
        )

    if estado_filtro:
        citas_filtradas = citas_mes.filter(estado_cita__icontains=estado_filtro)
    else:
        citas_filtradas = citas_mes

    total_citas_registradas = citas_mes.count()
    
    citas_atendidas_qs = citas_mes.filter(estado_cita__icontains='atendid')
    total_citas_atendidas = citas_atendidas_qs.count()

    citas_canceladas_qs = citas_mes.filter(estado_cita__icontains='cancel')
    total_citas_canceladas = citas_canceladas_qs.count()

    total_estudiantes_atendidos = citas_atendidas_qs.values('id_inscripcion__estudiante').distinct().count()

    informes_qs = Bitacora.objects.filter(
        Q(fecha_creacion__year=anio, fecha_creacion__month=mes) |
        Q(fecha_informe__year=anio, fecha_informe__month=mes)
    )
    if sexo_filtro:
        informes_qs = informes_qs.filter(
            Q(estudiante__persona__sexo__iexact=sexo_filtro) |
            Q(estudiante__persona__sexo__istartswith=sexo_filtro[0])
        )
    informes_generados = informes_qs.distinct().count()

    expedientes_qs = ExpedienteMultimedia.objects.filter(
        fecha_carga_archivo__year=anio, fecha_carga_archivo__month=mes
    )
    if sexo_filtro:
        expedientes_qs = expedientes_qs.filter(
            Q(estudiante__persona__sexo__iexact=sexo_filtro) |
            Q(estudiante__persona__sexo__istartswith=sexo_filtro[0])
        )
    
    # Se cuentan de forma única las carpetas de estudiantes (1 por estudiante)
    expedientes_generados = expedientes_qs.values('estudiante').distinct().count()

    ESTADOS_CITA = [
        ('Activo', 'Activo'),
        ('Atendido', 'Atendido'),
        ('Reagendado', 'Reagendado'),
        ('Cancelado', 'Cancelado'),
    ]

    OPCIONES_SEXO = [
        ('M', 'Masculino / Varón'),
        ('F', 'Femenino / Hembra'),
    ]

    citas_con_informe = []
    for cita in citas_filtradas.select_related('id_inscripcion__estudiante__persona'):
        estudiante_obj = None
        if hasattr(cita, 'id_inscripcion') and cita.id_inscripcion:
            estudiante_obj = getattr(cita.id_inscripcion, 'estudiante', None)

        informe_asociado = None

        if hasattr(Bitacora, 'cita'):
            informe_asociado = Bitacora.objects.filter(cita=cita).first()

        if not informe_asociado and estudiante_obj:
            informe_asociado = Bitacora.objects.filter(estudiante=estudiante_obj).first()

        if not informe_asociado and hasattr(Bitacora, 'inscripcion') and cita.id_inscripcion:
            informe_asociado = Bitacora.objects.filter(inscripcion=cita.id_inscripcion).first()

        citas_con_informe.append({
            'cita': cita,
            'bitacora': informe_asociado
        })

    context = {
        'mes_seleccionado': mes,
        'anio_seleccionado': anio,
        'estado_seleccionado': estado_filtro,
        'sexo_seleccionado': sexo_filtro,
        'estados_cita': ESTADOS_CITA,
        'opciones_sexo': OPCIONES_SEXO,
        'total_citas_registradas': total_citas_registradas,
        'total_citas_atendidas': total_citas_atendidas,
        'total_citas_canceladas': total_citas_canceladas,
        'total_estudiantes_atendidos': total_estudiantes_atendidos,
        'informes_generados': informes_generados,
        'expedientes_generados': expedientes_generados,
        'citas_listado_reporte': citas_con_informe,
    }
    
    return render(request, 'estudiantes/reportes.html', context)