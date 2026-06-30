from django import forms
from .models import Cliente


class ClienteCrearForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre_completo', 'documento', 'telefono',
            'correo', 'ciudad', 'direccion',
            'estado', 'observaciones'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'documento': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control rounded-3'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
            'estado': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
        }


class ClienteEditarForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'telefono', 'ciudad', 'direccion',
            'estado', 'observaciones'
        ]
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
            'estado': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 2}),
        }