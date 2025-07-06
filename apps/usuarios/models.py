from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
    """Modelo de usuário personalizado para o sistema"""
    
    TIPO_USUARIO_CHOICES = (
        ('admin', 'Administrador'),
        ('funcionario', 'Funcionário'),
        ('cliente', 'Cliente'),
        ('gerente', 'Gerente'),
    )
    
    # Campos básicos
    tipo_usuario = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente',
        help_text='Tipo de usuário no sistema'
    )
        
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Número de telefone para contato'
    )
    
    # Campos de sistema
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def nome_completo(self):
        """Método para retornar nome completo"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
class Cliente(models.Model):
    """Modelo para clientes"""
    
    TIPO_PESSOA_CHOICES = (
        ('fisica', 'Pessoa Física'),
        ('juridica', 'Pessoa Jurídica'),
    )
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuário',
        related_name='cliente_profile'
    )
    
    tipo_pessoa = models.CharField(
        'Tipo de Pessoa',
        max_length=10,
        choices=TIPO_PESSOA_CHOICES,
        default='fisica'
    )
    
    nome = models.CharField(
        'Nome/Razão Social',
        max_length=200,
        help_text='Nome completo ou razão social'
    )
    
    # Documentação
    bilhete_identidade = models.CharField(
        'Bilhete de Identidade',
        max_length=20,
        unique=True,
        blank=True,
        help_text='Número do Bilhete de Identidade'
    )
    
    data_nascimento = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True
    )
    
    # Contato
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    # Endereço
    endereco = models.TextField('Endereço', blank=True)
    
    # Informações adicionais
    profissao = models.CharField('Profissão', max_length=100, blank=True)
    
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Funcionario(models.Model):
    """Modelo para funcionários"""
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuário',
        related_name='funcionario_profile'
    )
    
    nome = models.CharField(
        'Nome Completo',
        max_length=200,
        help_text='Nome completo do funcionário'
    )
    
    bilhete_identidade = models.CharField(
        'Bilhete de Identidade',
        max_length=20,
        unique=True,
        help_text='Número do Bilhete de Identidade'
    )
    
    cargo = models.CharField(
        'Cargo',
        max_length=100,
        blank=True,
        help_text='Cargo do funcionário'
    )
    
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    comissao_venda = models.DecimalField(
        'Comissão de Venda (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentual de comissão sobre vendas'
    )
    
    data_admissao = models.DateField(
        'Data de Admissão',
        null=True,
        blank=True
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.cargo}"