from django import forms
from .models import Pedido, DetallePedido, METODO_PAGO_CHOICES, ESTADO_PEDIDO_CHOICES
from clientes.models import Cliente
from catalogo.models import Producto
from inventario.models import TALLAS_CHOICES


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'metodo_pago', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(estado='activo')


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'talla', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'talla': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control rounded-3', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['talla'].choices = TALLAS_CHOICES


class PedidoEstadoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'observaciones']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
        }