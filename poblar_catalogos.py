import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from estudiantes.models import (
    Municipio, Parroquia, Grado, Seccion, Escuela, PeriodoAcademico, AreaPatologica, Patologia
)

def poblar():
    print("Actualizando catálogos territoriales...")

    # 1. Limpiar municipios de prueba que no correspondan
    municipios_validos = ["José Antonio Páez", "Andrés Bello", "Pedro Gual"]
    Municipio.objects.exclude(nombre_municipio__in=municipios_validos).delete()

    # 2. MUNICIPIOS Y PARROQUIAS EXACTAS
    datos_territoriales = {
        "José Antonio Páez": [
            "Río Chico",
            "Paparo",
            "Tacarigua de La Laguna",
            "El Guapo",
            "San Fernando del Guapo"
        ],
        "Andrés Bello": [
            "San José de Barlovento",
            "Cumbo"
        ],
        "Pedro Gual": [
            "Cúpira",
            "Machurucuto"
        ]
    }

    for mun_nombre, parroquias_lista in datos_territoriales.items():
        municipio_obj, _ = Municipio.objects.get_or_create(nombre_municipio=mun_nombre)
        for par_nombre in parroquias_lista:
            Parroquia.objects.get_or_create(
                municipio=municipio_obj,
                nombre_parroquia=par_nombre
            )
    print("✓ Municipios y Parroquias actualizados con éxito.")

    # 3. GRADOS (1° a 6°)
    grados = ["1", "2", "3", "4", "5", "6"]
    for g in grados:
        Grado.objects.get_or_create(num_grado=g)
    print("✓ Grados listos.")

    # 4. SECCIONES (A a E)
    secciones = ["A", "B", "C", "D", "E", "U"]
    for s in secciones:
        Seccion.objects.get_or_create(letra_seccion=s)
    print("✓ Secciones listas.")

    # 5. PERÍODOS ACADÉMICOS
    periodos = [
        {"nombre": "2024-2025", "inicio": "2024-09-15", "final": "2025-07-31"},
        {"nombre": "2025-2026", "inicio": "2025-09-15", "final": "2026-07-31"},
        {"nombre": "2026-2027", "inicio": "2026-09-15", "final": "2027-07-31"},
    ]
    for p in periodos:
        PeriodoAcademico.objects.get_or_create(
            nombre_periodo=p["nombre"],
            defaults={"fecha_inicio": p["inicio"], "fecha_final": p["final"]}
        )
    print("✓ Períodos académicos listos.")

    # ESCUELAS POR MUNICIPIO
    escuelas_por_municipio = {
        "José Antonio Páez": [
            'U.E.E "J. Rio Chico"',
            'E.E.R "La Florida"',
            'C.E.I "Rio Chico"',
            'C.E "Las Delicias"',
            'C.E.E. "San Antonio"',
            'U.E.E "Rio Chico Arriba"',
            'E.B "Felipe Neri"',
            'C.E.E "El Guapo"',
            'C.N.E "Padre Zaldivar"',
            'E.E.B "El Cristo"',
            'E.B.E "Los Cerros"',
            'E.B.E "Cazaña"',
            'U.E.N "Rafael Arevalo Gonzalez"',
            'U.E.P "Jose Felix Ribas"',
            'U.E.P "13 de Junio"',
            'C.E.I.N "La Popita II"',
            'E.B.E "Juan Francisco de Leon"',
            'E.B.E "Valle de La Cruz"',
            'U.E.P "Juan Pablo de la Cruz"'
        ],
        "Andrés Bello": [
            'U.E.E "Escuraina Duque"',
            'U.E.N "Alfredo Jahn"',
            'E.B.E "Lander"',
            'E.E "Andres Bello"',
            'U.E.E "San Jose de Barlovento"'
        ],
        "Pedro Gual": [
            'U.E.N "Cupira"',
            'U.E. "8 de Diciembre"',
            'U.E.E "Juan Vicente Gonzalez"',
            'E.I.B N° 3932 "El Guacuco"',
            'U.E. "Palo Blanco"',
            'U.E.N.B "Calabaza"',
            'E.N.B "Bartolome Blandin"',
            'C.E.I.N.B "Cabo Codera"',
            'E.B.E "Chaguaramal"',
            'E.I.B "Pedro Gual"'
        ]
    }

    for mun_nombre, lista_escuelas in escuelas_por_municipio.items():
        try:
            mun_obj = Municipio.objects.get(nombre_municipio=mun_nombre)
            for esc_nombre in lista_escuelas:
                Escuela.objects.get_or_create(
                    nombre_escuela=esc_nombre,
                    municipio=mun_obj
                )
        except Municipio.DoesNotExist:
            pass
    print("✓ Listado completo de escuelas registrado y vinculado por municipio.")

    # 7. ÁREAS PATOLÓGICAS Y PATOLOGÍAS
    patologias_data = {
        "Cognitiva / Aprendizaje": [
            "Dificultad de Aprendizaje General",
            "Dislexia",
            "Discalculia",
            "TDAH (Déficit de Atención con Hiperactividad)"
        ],
        "Lenguaje y Comunicación": [
            "Dislalia",
            "Tartamudez (Disfemia)",
            "Trastorno del Desarrollo del Lenguaje (TDL)"
        ],
        "Conductual / Emocional": [
            "Trastorno de Conducta",
            "Ansiedad Escolar",
            "Baja Autoestima"
        ],
        "Desarrollo / Neurodiversidad": [
            "Trastorno del Espectro Autista (TEA)",
            "Compromiso Cognitivo Leve"
        ]
    }

    for area_nom, lista_pat in patologias_data.items():
        area_obj, _ = AreaPatologica.objects.get_or_create(nombre_area=area_nom)
        for pat_nom in lista_pat:
            Patologia.objects.get_or_create(
                area_patologica=area_obj,
                nombre_patologia=pat_nom
            )
    print("✓ Áreas y Patologías listas.")

if __name__ == '__main__':
    poblar()