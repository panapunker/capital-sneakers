from django import forms
from .models import Inventario, MovimientoInventario, TIPO_MOVIMIENTO_CHOICES


class AjusteInventarioForm(forms.Form):
    talla = forms.CharField(max_length=5)
    tipo = forms.ChoiceField(choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = forms.IntegerField(min_value=1)
    observacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )