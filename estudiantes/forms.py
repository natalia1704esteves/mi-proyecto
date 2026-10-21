from django import forms
from .models import Cita
from .models import Bitacora

class CitaForm(forms.ModelForm):
    # Definimos explícitamente las opciones con "Atendido" al lado de "Activo"
    ESTADOS_CITA = [
        ('Activo', 'Activo'),
        ('Atendido', 'Atendido'),
        ('Reagendado', 'Reagendado'),
        ('Cancelado', 'Cancelado'),
    ]
    
    estado_cita = forms.ChoiceField(
        choices=ESTADOS_CITA,
        widget=forms.RadioSelect(attrs={'class': 'estado-radio'}),
        initial='Activo'
    )

    class Meta:
        model = Cita
        fields = ['id_inscripcion', 'fecha_cita', 'hora', 'estado_cita', 'motivo_cita']
        widgets = {
            'id_inscripcion': forms.Select(attrs={'class': 'form-control-custom'}),
            'fecha_cita': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control-custom form-control-short', 'autocomplete': 'off'}),
            'hora': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-custom form-control-short'}),
            'motivo_cita': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3, 'placeholder': 'Motivo de la consulta...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_inscripcion'].label = "Buscar Estudiante (Cédula / Nombre)"
   