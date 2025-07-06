import os
import uuid
from django.db import models

from apps.veiculos.models import Carro
from apps.usuarios.models import Funcionario, Cliente

def documento_venda_path(instance, filename):
    """Caminho para upload de documentos de venda"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('vendas/documentos', filename)

class Venda(models.Model):
    """Modelo para vendas de carros"""
    
    TIPO_PAGAMENTO_CHOICES = (
        ('a_vista', 'À Vista'),
        ('financiado', 'Financiado'),
        ('misto', 'Misto'),
    )
    
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    )
    
    carro = models.ForeignKey(
        Carro,
        on_delete=models.CASCADE,
        verbose_name='Carro'
    )
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        verbose_name='Cliente'
    )
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário Responsável'
    )
    
    # Valores
    valor_venda = models.DecimalField(
        'Valor da Venda (Kz)',
        max_digits=12,
        decimal_places=2,
        help_text='Valor total da venda em Kwanza'
    )
    
    valor_entrada = models.DecimalField(
        'Valor de Entrada (Kz)',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    valor_financiado = models.DecimalField(
        'Valor Financiado (Kz)',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Pagamento
    tipo_pagamento = models.CharField(
        'Tipo de Pagamento',
        max_length=20,
        choices=TIPO_PAGAMENTO_CHOICES
    )
    
    forma_pagamento = models.CharField(
        'Forma de Pagamento',
        max_length=100,
        blank=True,
        help_text='Dinheiro, Transferência, Cartão, etc.'
    )
    
    banco_financiamento = models.CharField(
        'Banco de Financiamento',
        max_length=100,
        blank=True
    )
    
    numero_parcelas = models.PositiveIntegerField(
        'Número de Parcelas',
        null=True,
        blank=True
    )
    
    observacoes = models.TextField('Observações', blank=True)
    
    data_venda = models.DateTimeField('Data da Venda', auto_now_add=True)
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    
    class Meta:
        db_table = 'venda'
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda #{self.id} - {self.carro} - {self.cliente.nome}"


class DocumentoVenda(models.Model):
    """Modelo para documentos das vendas"""
    
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        verbose_name='Venda',
        related_name='documentos'
    )
    
    tipo_documento = models.CharField(
        'Tipo de Documento',
        max_length=100,
        help_text='Contrato, Nota Fiscal, etc.'
    )
    
    arquivo = models.FileField(
        'Arquivo',
        upload_to=documento_venda_path,
        help_text='Arquivo do documento'
    )
    
    data_upload = models.DateTimeField('Data de Upload', auto_now_add=True)
    
    class Meta:
        db_table = 'documento_venda'
        verbose_name = 'Documento de Venda'
        verbose_name_plural = 'Documentos de Vendas'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.tipo_documento} - Venda #{self.venda.id}"