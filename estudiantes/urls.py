from django.urls import path
from . import views
from .views import (
    registrar_estudiante_view, 
    listar_estudiantes_view, 
    editar_estudiante_view,  
    eliminar_estudiante_view
)

app_name = 'estudiantes'

urlpatterns = [
    # --- Rutas de Estudiantes ---
    path('registrar/', registrar_estudiante_view, name='registrar_estudiante'),
    path('listar/', listar_estudiantes_view, name='listar_estudiantes'),
    path('editar/<int:pk>/', editar_estudiante_view, name='editar_estudiante'),
    path('eliminar/<int:pk>/', eliminar_estudiante_view, name='eliminar_estudiante'),
    
# --- Rutas de Citas ---
 # --- Rutas de Citas ---
    path('citas/', views.listar_citas, name='listar_citas'),
    path('citas/registrar/', views.registrar_cita, name='registrar_cita'),
    path('citas/editar/<int:pk>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:pk>/', views.eliminar_cita, name='eliminar_cita'),

    # --- Rutas de Bitácoras / Informes ---
    path('bitacoras/', views.listar_bitacoras, name='listar_bitacoras'),
    path('bitacoras/buscar/', views.buscar_estudiante_bitacora, name='buscar_estudiante_bitacora'),
    path('bitacoras/redactar/<int:estudiante_id>/', views.redactar_informe_estudiante, name='crear_bitacora'),
    path('bitacoras/editar/<int:bitacora_id>/', views.editar_bitacora, name='editar_bitacora'),
    path('bitacoras/eliminar/<int:bitacora_id>/', views.eliminar_bitacora, name='eliminar_bitacora'),
    path('informes/redactar/<int:estudiante_id>/', views.redactar_informe_estudiante, name='redactar_informe_estudiante'),
    path('bitacora/<int:bitacora_id>/ver/', views.ver_bitacora, name='ver_bitacora'),
    path('patologia/crear-ajax/', views.crear_patologia_ajax, name='crear_patologia_ajax'),

    # --- Ruta de Expedientes Multimedia (¡Aquí dentro!) ---
   path('expedientes-multimedia/', views.modulo_expedientes_multimedia, name='expediente_multimedia'),
    # Vista 2: Vista individual interior de la carpeta del estudiante
    path('expedientes-multimedia/<int:estudiante_id>/', views.detalle_expediente_estudiante, name='detalle_expediente_estudiante'),

 # --- Ruta de Reportes
    path('reportes/', views.modulo_reportes, name='modulo_reportes'),

]