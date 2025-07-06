import os
import uuid
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

from apps.usuarios.models import Funcionario, Cliente
from apps.alugueis.models import Aluguel

def carro_foto_path(instance, filename):
    """Caminho para upload de fotos dos carros"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return f'projectos/django/concessionaria/media/carros/fotos/{filename}'
    #return os.path.join('carros/fotos', filename)
    
class Marca(models.Model):
    """Modelo para marcas de carros"""
    
    nome = models.CharField(
        'Nome',
        max_length=100,
        unique=True,
        help_text='Nome da marca'
    )
    
    pais_origem = models.CharField(
        'País de Origem',
        max_length=50,
        blank=True,
        help_text='País onde a marca foi fundada'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        db_table = 'marcas'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Modelo(models.Model):
    """Modelo para modelos de carros"""
    
    CATEGORIA_CHOICES = (
        ('sedan', 'Sedan'),
        ('hatch', 'Hatch'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup'),
        ('coupe', 'Coupé'),
        ('conversivel', 'Conversível'),
        ('minivan', 'Minivan'),
        ('outro', 'Outro'),
    )
    
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        verbose_name='Marca',
        related_name='modelos'
    )
    
    nome = models.CharField(
        'Nome',
        max_length=100,
        help_text='Nome do modelo'
    )
    
    categoria = models.CharField(
        'Categoria',
        max_length=20,
        choices=CATEGORIA_CHOICES,
        help_text='Categoria do veículo'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        db_table = 'modelos'
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        unique_together = ['marca', 'nome']
        ordering = ['marca__nome', 'nome']
    
    def __str__(self):
        return f"{self.marca.nome} {self.nome}"


class Cor(models.Model):
    """Modelo para cores dos carros"""
    
    nome = models.CharField(
        'Nome',
        max_length=50,
        unique=True,
        help_text='Nome da cor'
    )
    
    codigo_hex = models.CharField(
        'Código Hex',
        max_length=7,
        blank=True,
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'Formato inválido. Use #RRGGBB')],
        help_text='Código hexadecimal da cor (ex: #FF0000)'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        db_table = 'cor'
        verbose_name = 'Cor'
        verbose_name_plural = 'Cores'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Opcional(models.Model):
    """Modelo para opcionais/equipamentos dos carros"""
    
    nome = models.CharField(
        'Nome',
        max_length=100,
        unique=True,
        help_text='Nome do opcional'
    )
    
    categoria = models.CharField(
        'Categoria',
        max_length=50,
        blank=True,
        help_text='Categoria do opcional (ex: Segurança, Conforto, Tecnologia)'
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada do opcional'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        db_table = 'opcional'
        verbose_name = 'Opcional'
        verbose_name_plural = 'Opcionais'
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return self.nome


class Carro(models.Model):
    """Modelo principal para carros"""
    
    CONDICAO_CHOICES = (
        ('novo', 'Novo'),
        ('usado', 'Usado'),
    )
    
    COMBUSTIVEL_CHOICES = (
        ('gasolina', 'Gasolina'),
        ('etanol', 'Etanol'),
        ('flex', 'Flex'),
        ('diesel', 'Diesel'),
        ('eletrico', 'Elétrico'),
        ('hibrido', 'Híbrido'),
    )
    
    TRANSMISSAO_CHOICES = (
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
        ('cvt', 'CVT'),
        ('automatizado', 'Automatizado'),
    )
    
    # Relacionamentos
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.CASCADE,
        verbose_name='Modelo',
        related_name='carros'
    )
    
    cor = models.ForeignKey(
        Cor,
        on_delete=models.CASCADE,
        verbose_name='Cor',
        related_name='carros'
    )
    
    opcionais = models.ManyToManyField(
        Opcional,
        blank=True,
        verbose_name='Opcionais',
        related_name='carros'
    )
    
    # Informações básicas
    ano_fabricacao = models.PositiveIntegerField(
        'Ano de Fabricação',
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 1)
        ]
    )
    
    ano_modelo = models.PositiveIntegerField(
        'Ano do Modelo',
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 2)
        ]
    )
    
    condicao = models.CharField(
        'Condição',
        max_length=10,
        choices=CONDICAO_CHOICES,
        help_text='Condição do veículo'
    )
    
    # Preços
    preco_venda = models.DecimalField(
        'Preço de Venda (Kz)',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Preço de venda em Kwanza'
    )
    
    preco_aluguel_diario = models.DecimalField(
        'Preço Aluguel Diário (Kz)',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Preço de aluguel por dia em Kwanza'
    )
    
    # Especificações técnicas
    quilometragem = models.PositiveIntegerField(
        'Quilometragem',
        default=0,
        help_text='Quilometragem atual do veículo'
    )
    
    combustivel = models.CharField(
        'Combustível',
        max_length=20,
        choices=COMBUSTIVEL_CHOICES
    )
    
    transmissao = models.CharField(
        'Transmissão',
        max_length=20,
        choices=TRANSMISSAO_CHOICES
    )
    
    motor = models.CharField(
        'Motor',
        max_length=20,
        blank=True,
        help_text='Especificação do motor (ex: 1.0, 1.6, 2.0)'
    )
    
    numero_portas = models.PositiveSmallIntegerField(
        'Número de Portas',
        null=True,
        blank=True,
        validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    
    # Documentação
    chassi = models.CharField(
        'Chassi',
        max_length=17,
        unique=True,
        blank=True,
        help_text='Número do chassi (17 dígitos)'
    )
    
    matricula = models.CharField(
        'Matrícula',
        max_length=15,
        unique=True,
        blank=True,
        help_text='Matrícula do veículo em Angola'
    )
    
    documento_unico = models.CharField(
        'Documento Único',
        max_length=20,
        blank=True,
        help_text='Número do Documento Único Automóvel'
    )
    
    # Disponibilidade
    disponivel_venda = models.BooleanField('Disponível para Venda', default=True)
    disponivel_aluguel = models.BooleanField('Disponível para Aluguel', default=True)
    
    # Descrições
    descricao = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição detalhada do veículo'
    )
    
    observacoes = models.TextField(
        'Observações',
        blank=True,
        help_text='Observações internas'
    )
    
    # Campos de sistema
    data_entrada = models.DateTimeField('Data de Entrada', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        db_table = 'carros'
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'
        ordering = ['-data_entrada']
    
    def __str__(self):
        return f"{self.modelo} {self.ano_modelo} - {self.cor}"
    
    @property
    def nome_completo(self):
        return f"{self.modelo.marca.nome} {self.modelo.nome} {self.ano_modelo}"


class FotoCarro(models.Model):
    """Modelo para fotos dos carros"""
    
    carro = models.ForeignKey(
        Carro,
        on_delete=models.CASCADE,
        verbose_name='Carro',
        related_name='fotos'
    )
    
    foto = models.ImageField(
        'Foto',
        upload_to=carro_foto_path,
        help_text='Foto do veículo'
    )
    
    descricao = models.CharField(
        'Descrição',
        max_length=200,
        blank=True,
        help_text='Descrição da foto'
    )
    
    ordem = models.PositiveSmallIntegerField(
        'Ordem',
        default=1,
        help_text='Ordem de exibição da foto'
    )
    
    foto_principal = models.BooleanField(
        'Foto Principal',
        default=False,
        help_text='Marcar como foto principal'
    )
    
    data_upload = models.DateTimeField('Data de Upload', auto_now_add=True)
    
    class Meta:
        db_table = 'foto_carro'
        verbose_name = 'Foto do Carro'
        verbose_name_plural = 'Fotos dos Carros'
        ordering = ['ordem', 'data_upload']
    
    def __str__(self):
        return f"Foto {self.ordem} - {self.carro}"

class MovimentacaoEstoque(models.Model):
    """Modelo para controle de movimentação de estoque de carros"""
    
    TIPO_MOVIMENTACAO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida_venda', 'Saída - Venda'),
        ('saida_aluguel', 'Saída - Aluguel'),
        ('retorno_aluguel', 'Retorno - Aluguel'),
        ('transferencia', 'Transferência'),
        ('baixa', 'Baixa'),
    )
    
    carro = models.ForeignKey(
        Carro,
        on_delete=models.CASCADE,
        verbose_name='Carro',
        related_name='movimentacoes'
    )
    
    tipo_movimentacao = models.CharField(
        'Tipo de Movimentação',
        max_length=20,
        choices=TIPO_MOVIMENTACAO_CHOICES
    )
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário Responsável'
    )
    
    observacoes = models.TextField(
        'Observações',
        blank=True,
        help_text='Observações sobre a movimentação'
    )
    
    data_movimentacao = models.DateTimeField('Data da Movimentação', auto_now_add=True)
    
    # Referências para documentos relacionados
    venda = models.ForeignKey(
        'vendas.Venda', # string para referência para evitar o erro da importacao circular
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Venda Relacionada'
    )
    
    aluguel = models.ForeignKey(
        Aluguel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Aluguel Relacionado'
    )
    
    class Meta:
        db_table = 'movimentacao_estoque'
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data_movimentacao']
    
    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} - {self.carro} - {self.data_movimentacao.strftime('%d/%m/%Y')}"


class HistoricoStatusCarro(models.Model):
    """Modelo para histórico de mudanças de status dos carros"""
    
    carro = models.ForeignKey(
        Carro,  
        on_delete=models.CASCADE,
        verbose_name='Carro',
        related_name='historico_status'
    )
    status_anterior = models.CharField(
        'Status Anterior',
        max_length=50,
        null=True,
        blank=True,
        help_text='Status anterior do carro'
    )
    status_novo = models.CharField(
        'Status Novo',
        max_length=50,
        null=True,
        blank=True,
        help_text='Novo status do carro'
    )
    motivo = models.TextField(
        'Motivo',
        null=True,
        blank=True,
        help_text='Motivo da mudança de status'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário Responsável'
    )
    
    data_alteracao = models.DateTimeField(
        'Data da Alteração',
        default=timezone.now,
        help_text='Data e hora da alteração do status'
    )

    class Meta:
        db_table = 'historico_status_carro'
        verbose_name = 'Histórico de Status do Carro'
        verbose_name_plural = 'Históricos de Status dos Carros'
        ordering = ['-data_alteracao']
        db_table = 'historico_status_carros'

    def __str__(self):
        return f'{self.carro} - {self.status_anterior} → {self.status_novo} - {self.data_alteracao.strftime("%d/%m/%Y %H:%M")}'


class Manutencao(models.Model):
    """Modelo para manutenções dos carros"""
    
    TIPO_MANUTENCAO_CHOICES = (
        ('preventiva', 'Preventiva'),
        ('corretiva', 'Corretiva'),
        ('revisao', 'Revisão'),
    )
    
    carro = models.ForeignKey(
        Carro,
        on_delete=models.CASCADE,
        verbose_name='Carro',
        related_name='manutencoes'
    )
    
    tipo_manutencao = models.CharField(
        'Tipo de Manutenção',
        max_length=20,
        choices=TIPO_MANUTENCAO_CHOICES
    )
    
    descricao = models.TextField(
        'Descrição',
        help_text='Descrição detalhada da manutenção'
    )
    
    valor = models.DecimalField(
        'Valor (Kz)',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Valor da manutenção em Kwanza'
    )
    
    quilometragem = models.PositiveIntegerField(
        'Quilometragem',
        null=True,
        blank=True,
        help_text='Quilometragem no momento da manutenção'
    )
    
    oficina = models.CharField(
        'Oficina',
        max_length=200,
        blank=True,
        help_text='Nome da oficina onde foi realizada'
    )
    
    data_manutencao = models.DateField(
        'Data da Manutenção',
        help_text='Data em que a manutenção foi realizada'
    )
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        default=timezone.now,
        help_text='Data e hora do cadastro no sistema'
    )

    class Meta:
        db_table = 'manutencao'
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
        ordering = ['-data_manutencao', '-data_cadastro']
        db_table = 'manutencoes'

    def __str__(self):
        return f'{self.get_tipo_manutencao_display()} - {self.carro} - {self.data_manutencao}'
