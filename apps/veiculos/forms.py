# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Carro, Marca, Modelo, Cor, Opcional, FotoCarro
from django.core.validators import RegexValidator

class CarroRegistroForm(forms.ModelForm):
    primeira_foto = forms.ImageField(
        label='Primeira Foto do Carro',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )
    
    class Meta:
        model = Carro
        fields = [
            'modelo', 'cor', 'ano_fabricacao', 'ano_modelo', 'condicao',
            'preco_venda', 'preco_aluguel_diario', 'quilometragem',
            'combustivel', 'transmissao', 'motor', 'numero_portas',
            'chassi', 'matricula', 'documento_unico', 
            'disponivel_venda', 'disponivel_aluguel', 'descricao', 'observacoes'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
            'preco_venda': forms.NumberInput(attrs={'step': '0.01'}),
            'preco_aluguel_diario': forms.NumberInput(attrs={'step': '0.01'}),
            'ano_fabricacao': forms.NumberInput(),
            'ano_modelo': forms.NumberInput(),
            'quilometragem': forms.NumberInput(),
            'numero_portas': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas modelos de marcas ativas
        self.fields['modelo'].queryset = Modelo.objects.filter(
            ativo=True, 
            marca__ativo=True
        ).select_related('marca')
        
        # Filtrar apenas cores ativas
        self.fields['cor'].queryset = Cor.objects.filter(ativo=True)
        
        # Adiciona classes Bootstrap para validação e estilo
        for field_name, field in self.fields.items():
            if field_name in ['disponivel_venda', 'disponivel_aluguel']:
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Ajustar alguns campos específicos
        self.fields['modelo'].widget.attrs['class'] = 'form-select'
        self.fields['cor'].widget.attrs['class'] = 'form-select'
        self.fields['condicao'].widget.attrs['class'] = 'form-select'
        self.fields['combustivel'].widget.attrs['class'] = 'form-select'
        self.fields['transmissao'].widget.attrs['class'] = 'form-select'
        
        # Placeholders úteis
        self.fields['chassi'].widget.attrs['placeholder'] = '17 dígitos do chassi'
        self.fields['matricula'].widget.attrs['placeholder'] = 'Ex: LD-12-34-AB'
        self.fields['motor'].widget.attrs['placeholder'] = 'Ex: 1.0, 1.6, 2.0'
        self.fields['preco_venda'].widget.attrs['placeholder'] = '0.00'
        self.fields['preco_aluguel_diario'].widget.attrs['placeholder'] = '0.00'

    def clean_chassi(self):
        chassi = self.cleaned_data.get('chassi')
        if chassi and len(chassi) != 17:
            raise forms.ValidationError('O chassi deve ter exatamente 17 caracteres.')
        return chassi
    
    def clean_ano_fabricacao(self):
        ano_fabricacao = self.cleaned_data.get('ano_fabricacao')
        ano_modelo = self.cleaned_data.get('ano_modelo')
        
        if ano_fabricacao and ano_modelo and ano_fabricacao > ano_modelo:
            raise forms.ValidationError('Ano de fabricação não pode ser maior que o ano do modelo.')
        
        return ano_fabricacao
    
class MarcaRegistroForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'pais_origem', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da marca'
            }),
            'pais_origem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País de origem (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'required': True})


class ModeloRegistroForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['marca', 'nome', 'categoria', 'ativo']
        widgets = {
            'marca': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do modelo'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas marcas ativas
        self.fields['marca'].queryset = Marca.objects.filter(ativo=True)
        self.fields['nome'].widget.attrs.update({'required': True})


class CorRegistroForm(forms.ModelForm):
    class Meta:
        model = Cor
        fields = ['nome', 'codigo_hex', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da cor'
            }),
            'codigo_hex': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '#FFFFFF',
                'pattern': '#[0-9A-Fa-f]{6}'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'required': True})