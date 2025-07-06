import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

def usuario_foto_path(instance, filename):
    """Caminho para upload de foto de perfil do usuário"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('usuarios/perfil', filename)

def carro_foto_path(instance, filename):
    """Caminho para upload de fotos dos carros"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('carros/fotos', filename)

def documento_venda_path(instance, filename):
    """Caminho para upload de documentos de venda"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('vendas/documentos', filename)

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
    
    # Informações pessoais
    nome_completo = models.CharField(
        'Nome Completo',
        max_length=200,
        help_text='Nome completo do usuário'
    )
    
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Número de telefone para contato'
    )
    
    # Documentação angolana
    bilhete_identidade = models.CharField(
        'Bilhete de Identidade',
        max_length=20,
        blank=True,
        unique=True,
        help_text='Número do Bilhete de Identidade'
    )
    
    nif = models.CharField(
        'NIF',
        max_length=20,
        blank=True,
        unique=True,
        help_text='Número de Identificação Fiscal'
    )
    
    # Endereço angolano
    provincia = models.CharField(
        'Província',
        max_length=50,
        blank=True,
        help_text='Província de Angola'
    )
    
    municipio = models.CharField(
        'Município',
        max_length=100,
        blank=True,
        help_text='Município'
    )
    
    endereco_completo = models.TextField(
        'Endereço Completo',
        blank=True,
        help_text='Endereço completo'
    )
    
    # Mídia
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to=usuario_foto_path,
        blank=True,
        null=True,
        help_text='Foto de perfil do usuário'
    )
    
    # Campos de sistema
    ativo = models.BooleanField('Ativo', default=True)
    data_manutencao = models.DateField(
        'Data da Manutenção',
        help_text='Data em que a manutenção foi realizada'
    )
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
        ordering = ['-data_manutencao']
    
    def __str__(self):
        return f"{self.get_tipo_manutencao_display()} - {self.carro} - {self.data_manutencao}"


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
        blank=True,
        help_text='Status anterior do carro'
    )
    
    status_novo = models.CharField(
        'Status Novo',
        max_length=50,
        help_text='Novo status do carro'
    )
    
    motivo = models.TextField(
        'Motivo',
        blank=True,
        help_text='Motivo da alteração de status'
    )
    
    usuario = models.CharField(
        'Usuário',
        max_length=100,
        blank=True,
        help_text='Usuário que realizou a alteração'
    )
    
    data_alteracao = models.DateTimeField('Data da Alteração', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico de Status do Carro'
        verbose_name_plural = 'Histórico de Status dos Carros'
        ordering = ['-data_alteracao']
    
    def __str__(self):
        return f"{self.carro} - {self.status_anterior} → {self.status_novo}"


class Configuracao(models.Model):
    """Modelo para configurações do sistema"""
    
    chave = models.CharField(
        'Chave',
        max_length=100,
        unique=True,
        help_text='Chave da configuração'
    )
    
    valor = models.TextField(
        'Valor',
        blank=True,
        help_text='Valor da configuração'
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        help_text='Descrição da configuração'
    )
    
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'
        ordering = ['chave']
    
    def __str__(self):
        return f"{self.chave}: {self.valor}"


# Modelo adicional para Angola - Províncias
class Provincia(models.Model):
    """Modelo para províncias de Angola"""
    
    nome = models.CharField(
        'Nome',
        max_length=50,
        unique=True,
        help_text='Nome da província'
    )
    
    codigo = models.CharField(
        'Código',
        max_length=5,
        unique=True,
        blank=True,
        help_text='Código da província'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Província'
        verbose_name_plural = 'Províncias'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Municipio(models.Model):
    """Modelo para municípios de Angola"""
    
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        verbose_name='Província',
        related_name='municipios'
    )
    
    nome = models.CharField(
        'Nome',
        max_length=100,
        help_text='Nome do município'
    )
    
    codigo = models.CharField(
        'Código',
        max_length=10,
        blank=True,
        help_text='Código do município'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Município'
        verbose_name_plural = 'Municípios'
        unique_together = ['provincia', 'nome']
        ordering = ['provincia__nome', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.provincia.nome}"


# Modelo adicional para controle de estoque
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
        Venda,
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
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data_movimentacao']
    
    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} - {self.carro} - {self.data_movimentacao.strftime('%d/%m/%Y')}"


# Modelo para relatórios de performance
class RelatorioVendas(models.Model):
    """Modelo para relatórios de vendas (pode ser usado para dashboards)"""
    
    PERIODO_CHOICES = (
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    )
    
    periodo = models.CharField(
        'Período',
        max_length=10,
        choices=PERIODO_CHOICES
    )
    
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Funcionário'
    )
    
    # Métricas de vendas
    quantidade_vendas = models.PositiveIntegerField('Quantidade de Vendas', default=0)
    valor_total_vendas = models.DecimalField(
        'Valor Total de Vendas (Kz)',
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    valor_comissoes = models.DecimalField(
        'Valor das Comissões (Kz)',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Métricas de aluguel
    quantidade_alugueis = models.PositiveIntegerField('Quantidade de Aluguéis', default=0)
    valor_total_alugueis = models.DecimalField(
        'Valor Total de Aluguéis (Kz)',
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    data_geracao = models.DateTimeField('Data de Geração', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Relatório de Vendas'
        verbose_name_plural = 'Relatórios de Vendas'
        ordering = ['-data_geracao']
    
    def __str__(self):
        if self.funcionario:
            return f"Relatório {self.get_periodo_display()} - {self.funcionario.nome} - {self.data_inicio} a {self.data_fim}"
        return f"Relatório {self.get_periodo_display()} - Geral - {self.data_inicio} a {self.data_fim}"


# Signals para automatizar algumas operações
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(post_save, sender=Venda)
def atualizar_disponibilidade_carro_venda(sender, instance, created, **kwargs):
    """Atualiza disponibilidade do carro após venda"""
    if created and instance.status == 'finalizada':
        instance.carro.disponivel_venda = False
        instance.carro.save()

@receiver(post_save, sender=Aluguel)
def atualizar_disponibilidade_carro_aluguel(sender, instance, created, **kwargs):
    """Atualiza disponibilidade do carro para aluguel"""
    if instance.status == 'ativo':
        instance.carro.disponivel_aluguel = False
        instance.carro.save()
    elif instance.status in ['finalizado', 'cancelado']:
        instance.carro.disponivel_aluguel = True
        instance.carro.save()

@receiver(pre_save, sender=FotoCarro)
def garantir_foto_principal_unica(sender, instance, **kwargs):
    """Garante que apenas uma foto seja marcada como principal por carro"""
    if instance.foto_principal:
        FotoCarro.objects.filter(
            carro=instance.carro,
            foto_principal=True
        ).exclude(id=instance.id).update(foto_principal=False)criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.nome_completo} ({self.get_tipo_usuario_display()})"


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
        verbose_name = 'Foto do Carro'
        verbose_name_plural = 'Fotos dos Carros'
        ordering = ['ordem', 'data_upload']
    
    def __str__(self):
        return f"Foto {self.ordem} - {self.carro}"


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
    
    nif = models.CharField(
        'NIF',
        max_length=20,
        unique=True,
        blank=True,
        help_text='Número de Identificação Fiscal'
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
    
    # Endereço angolano
    endereco = models.TextField('Endereço', blank=True)
    provincia = models.CharField('Província', max_length=50, blank=True)
    municipio = models.CharField('Município', max_length=100, blank=True)
    
    # Informações adicionais
    profissao = models.CharField('Profissão', max_length=100, blank=True)
    renda_mensal = models.DecimalField(
        'Renda Mensal (Kz)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
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
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.cargo}"


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
        verbose_name = 'Documento de Venda'
        verbose_name_plural = 'Documentos de Vendas'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.tipo_documento} - Venda #{self.venda.id}"


class Aluguel(models.Model):
    """Modelo para aluguéis de carros"""
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('atrasado', 'Atrasado'),
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
        verbose_name = 'Pagamento de Aluguel'
        verbose_name_plural = 'Pagamentos de Aluguéis'
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f"Pagamento Aluguel #{self.aluguel.id} - {self.valor} Kz"


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
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
        ordering = ['-data_manutencao', '-data_cadastro']
        db_table = 'manutencoes'

    def __str__(self):
        return f'{self.get_tipo_manutencao_display()} - {self.carro} - {self.data_manutencao}'

class HistoricoStatusCarro(models.Model):
    """Modelo para histórico de mudanças de status dos carros"""
    
    carro = models.ForeignKey(
        'Carro',  # Assumindo que existe um modelo Carro
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
    usuario = models.CharField(
        'Usuário',
        max_length=100,
        null=True,
        blank=True,
        help_text='Usuário que realizou a alteração'
    )
    data_alteracao = models.DateTimeField(
        'Data da Alteração',
        default=timezone.now,
        help_text='Data e hora da alteração do status'
    )

    class Meta:
        verbose_name = 'Histórico de Status do Carro'
        verbose_name_plural = 'Históricos de Status dos Carros'
        ordering = ['-data_alteracao']
        db_table = 'historico_status_carros'

    def __str__(self):
        return f'{self.carro} - {self.status_anterior} → {self.status_novo} - {self.data_alteracao.strftime("%d/%m/%Y %H:%M")}'


class Configuracao(models.Model):
    """Modelo para configurações do sistema"""
    
    chave = models.CharField(
        'Chave',
        max_length=100,
        unique=True,
        help_text='Chave única da configuração'
    )
    valor = models.TextField(
        'Valor',
        null=True,
        blank=True,
        help_text='Valor da configuração'
    )
    descricao = models.TextField(
        'Descrição',
        null=True,
        blank=True,
        help_text='Descrição da configuração'
    )
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True,
        help_text='Data e hora da última atualização'
    )

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'
        ordering = ['chave']
        db_table = 'configuracoes'

    def __str__(self):
        return f'{self.chave}: {self.valor}'

    def save(self, *args, **kwargs):
        """Override do save para garantir que a data_atualizacao seja atualizada"""
        super().save(*args, **kwargs)