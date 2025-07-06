from django.db import models
from apps.usuarios.models import Cliente, Funcionario

class Aluguel(models.Model):
    """Modelo para aluguéis de carros"""
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('atrasado', 'Atrasado'),
    )
    
    carro = models.ForeignKey(
        'veiculos.Carro', # string para referência para evitar o erro da importacao circular
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
    
    # Datas
    data_inicio = models.DateField('Data de Início')
    data_fim_prevista = models.DateField('Data de Fim Prevista')
    data_fim_real = models.DateField('Data de Fim Real', null=True, blank=True)
    
    # Valores
    valor_diario = models.DecimalField(
        'Valor Diário (Kz)',
        max_digits=8,
        decimal_places=2,
        help_text='Valor do aluguel por dia em Kwanza'
    )
    
    valor_total_previsto = models.DecimalField(
        'Valor Total Previsto (Kz)',
        max_digits=10,
        decimal_places=2
    )
    
    valor_total_final = models.DecimalField(
        'Valor Total Final (Kz)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Quilometragem
    quilometragem_inicial = models.PositiveIntegerField(
        'Quilometragem Inicial',
        null=True,
        blank=True
    )
    
    quilometragem_final = models.PositiveIntegerField(
        'Quilometragem Final',
        null=True,
        blank=True
    )
    
    # Caução
    deposito_caucao = models.DecimalField(
        'Depósito Caução (Kz)',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Observações
    observacoes_entrega = models.TextField('Observações de Entrega', blank=True)
    observacoes_devolucao = models.TextField('Observações de Devolução', blank=True)
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='ativo'
    )
    
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        db_table = 'aluguel'
        verbose_name = 'Aluguel'
        verbose_name_plural = 'Aluguéis'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Aluguel #{self.id} - {self.carro} - {self.cliente.nome}"


class PagamentoAluguel(models.Model):
    """Modelo para pagamentos de aluguel"""
    
    aluguel = models.ForeignKey(
        Aluguel,
        on_delete=models.CASCADE,
        verbose_name='Aluguel',
        related_name='pagamentos'
    )
    
    valor = models.DecimalField(
        'Valor (Kz)',
        max_digits=10,
        decimal_places=2,
        help_text='Valor do pagamento em Kwanza'
    )
    
    tipo_pagamento = models.CharField(
        'Tipo de Pagamento',
        max_length=50,
        blank=True,
        help_text='Diário, Semanal, Total, etc.'
    )
    
    forma_pagamento = models.CharField(
        'Forma de Pagamento',
        max_length=100,
        blank=True,
        help_text='Dinheiro, Transferência, Cartão, etc.'
    )
    
    data_pagamento = models.DateTimeField('Data de Pagamento', auto_now_add=True)
    observacoes = models.TextField('Observações', blank=True)
    
    class Meta:
        db_table = 'pagamento_aluguel'
        verbose_name = 'Pagamento de Aluguel'
        verbose_name_plural = 'Pagamentos de Aluguéis'
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f"Pagamento Aluguel #{self.aluguel.id} - {self.valor} Kz"
