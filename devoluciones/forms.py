from django import forms
from .models import (
    Devolucion,
    DetalleDevolucion,
    TIPO_DEVOLUCION_CHOICES,
    ESTADO_PRODUCTO_CHOICES,
)
from inventario.models import TALLAS_CHOICES


class DevolucionForm(forms.ModelForm):
    """
    Formulario de cabecera de la devolución.
    El pedido y cliente se asignan en la vista, no aquí,
    porque dependen del pedido seleccionado previamente.
    """
    class Meta:
        model = Devolucion
        fields = ['tipo', 'motivo', 'observaciones']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el motivo general de la devolución...',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales (opcional)...',
            }),
        }
        labels = {
            'tipo': 'Tipo de devolución',
            'motivo': 'Motivo',
            'observaciones': 'Observaciones',
        }


class DetalleDevolucionForm(forms.ModelForm):
    """
    Formulario de línea de producto a devolver.
    Se usa dentro de un formset (uno por cada DetallePedido seleccionado).
    """
    class Meta:
        model = DetalleDevolucion
        fields = [
            'detalle_pedido', 'producto', 'talla', 'cantidad',
            'motivo', 'estado_producto', 'vuelve_a_inventario',
            'talla_nueva', 'producto_nuevo',
        ]
        widgets = {
            'detalle_pedido': forms.HiddenInput(),
            'producto': forms.HiddenInput(),
            'talla': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motivo específico (opcional)',
            }),
            'estado_producto': forms.Select(attrs={'class': 'form-select'}),
            'vuelve_a_inventario': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'talla_nueva': forms.Select(attrs={'class': 'form-select'}),
            'producto_nuevo': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        cantidad = cleaned.get('cantidad')
        detalle_pedido = cleaned.get('detalle_pedido')

        if cantidad and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a cero.')

        if cantidad and detalle_pedido and cantidad > detalle_pedido.cantidad:
            raise forms.ValidationError(
                f'No puedes devolver más unidades ({cantidad}) que las '
                f'compradas en el pedido ({detalle_pedido.cantidad}).'
            )

        estado_producto = cleaned.get('estado_producto')
        if estado_producto in ('defectuoso', 'danado'):
            cleaned['vuelve_a_inventario'] = False

        return cleaned


# ── Formset para múltiples productos por devolución ─────────────────────
DetalleDevolucionFormSet = forms.modelformset_factory(
    DetalleDevolucion,
    form=DetalleDevolucionForm,
    extra=0,
    can_delete=False,
)


class FiltroDevolucionForm(forms.Form):
    """
    Formulario de filtros para el listado de devoluciones.
    Reutilizable por: Listado, Reportes.
    """
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre o documento del cliente',
        })
    )
    pedido_id = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '# Pedido',
        })
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Devolucion._meta.get_field('estado').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + TIPO_DEVOLUCION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por texto...',
        })
    )