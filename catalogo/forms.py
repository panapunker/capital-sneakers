from django import forms
from .models import Categoria, Marca, Producto


TALLAS_POR_GENERO = {
    'dama': ['36', '37', '38', '39'],
    'caballero': ['40', '41', '42', '43', '44', '45'],
    'nino': ['28', '30', '32', '33', '34', '35'],
    'ambos': ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45'],
}


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la marca'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'marca', 'categoria', 'referencia',
            'precio_compra', 'precio_venta', 'genero',
            'imagen_principal', 'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referencia única'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'genero': forms.Select(attrs={'class': 'form-select', 'id': 'id_genero'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['marca'].queryset = Marca.objects.filter(activo=True)
        self.fields['categoria'].queryset = Categoria.objects.filter(activo=True)
        self.fields['marca'].empty_label = 'Seleccione una marca'
        self.fields['categoria'].empty_label = 'Seleccione una categoría'
        self.fields['genero'].widget.attrs['onchange'] = 'cargarTallas(this.value)'