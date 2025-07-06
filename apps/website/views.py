from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.core.paginator import Paginator
from apps.veiculos.models import Carro, Marca, Cor, Modelo, FotoCarro
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q, Count

def home_view(request):
    return render(request, 'website/home.html')

def sobre_view(request):
    return render(request, 'website/sobre.html')

def contacto_view(request):
    return render(request, 'website/contacto.html')

def loja_view(request):
    return render(request, 'website/loja.html')

def detalhes_veiculo_view(request):
    return render(request, 'website/detalhe.html')

def login_website_view(request):
    return render(request, 'website/login.html')

def cadastro_view(request):
    return render(request, 'website/cadastro.html')

class HomeView(TemplateView):
    template_name = 'website/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Carros em destaque (mais recentes disponíveis para venda)
        carros_destaque = Carro.objects.select_related(
            'modelo__marca', 'cor'
        ).prefetch_related('fotos').filter(
            disponivel_venda=True
        ).order_by('-data_entrada')[:6]
        
        # Estatísticas gerais
        context['total_carros'] = Carro.objects.filter(disponivel_venda=True).count()
        context['total_marcas'] = Marca.objects.filter(ativo=True).count()
        context['carros_novos'] = Carro.objects.filter(
            disponivel_venda=True, 
            condicao='novo'
        ).count()
        context['carros_usados'] = Carro.objects.filter(
            disponivel_venda=True, 
            condicao='usado'
        ).count()
        
        # Carros em destaque
        context['carros_destaque'] = carros_destaque
        
        # Marcas mais populares (com mais carros disponíveis)
        marcas_populares = Marca.objects.filter(
            ativo=True,
            modelos__carros__disponivel_venda=True
        ).distinct().annotate(
            total_carros=Count('modelos__carros', 
                                    filter=Q(modelos__carros__disponivel_venda=True))
        ).order_by('-total_carros')[:8]
        
        context['marcas_populares'] = marcas_populares
        
        return context

class CarroListView(ListView):
    model = Carro
    template_name = 'website/loja.html'
    context_object_name = 'carros'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Carro.objects.select_related(
            'modelo__marca', 'cor'
        ).prefetch_related('fotos', 'opcionais').filter(
            disponivel_venda=True
        )
        
        # Filtros de busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(modelo__nome__icontains=search) |
                Q(modelo__marca__nome__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        # Filtro por marca
        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(modelo__marca__id=marca)
        
        # Filtro por cor
        cor = self.request.GET.get('cor')
        if cor:
            queryset = queryset.filter(cor__id=cor)
        
        # Filtro por condição
        condicao = self.request.GET.get('condicao')
        if condicao:
            queryset = queryset.filter(condicao=condicao)
        
        # Filtro por combustível
        combustivel = self.request.GET.get('combustivel')
        if combustivel:
            queryset = queryset.filter(combustivel=combustivel)
        
        # Filtro por transmissão
        transmissao = self.request.GET.get('transmissao')
        if transmissao:
            queryset = queryset.filter(transmissao=transmissao)
        
        # Filtro por ano
        ano_min = self.request.GET.get('ano_min')
        ano_max = self.request.GET.get('ano_max')
        if ano_min:
            queryset = queryset.filter(ano_modelo__gte=ano_min)
        if ano_max:
            queryset = queryset.filter(ano_modelo__lte=ano_max)
        
        # Filtro por preço
        preco_min = self.request.GET.get('preco_min')
        preco_max = self.request.GET.get('preco_max')
        if preco_min:
            queryset = queryset.filter(preco_venda__gte=preco_min)
        if preco_max:
            queryset = queryset.filter(preco_venda__lte=preco_max)
        
        # Ordenação
        ordenacao = self.request.GET.get('ordem', '-data_entrada')
        ordenacao_opcoes = {
            'preco_asc': 'preco_venda',
            'preco_desc': '-preco_venda',
            'ano_asc': 'ano_modelo',
            'ano_desc': '-ano_modelo',
            'km_asc': 'quilometragem',
            'km_desc': '-quilometragem',
            'recente': '-data_entrada',
            'antigo': 'data_entrada',
        }
        
        if ordenacao in ordenacao_opcoes:
            queryset = queryset.order_by(ordenacao_opcoes[ordenacao])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar dados para os filtros
        context['marcas'] = Marca.objects.filter(ativo=True).order_by('nome')
        context['cores'] = Cor.objects.filter(ativo=True).order_by('nome')
        context['condicoes'] = Carro.CONDICAO_CHOICES
        context['combustiveis'] = Carro.COMBUSTIVEL_CHOICES
        context['transmissoes'] = Carro.TRANSMISSAO_CHOICES
        
        # Manter valores dos filtros no contexto
        context['filtros_ativos'] = {
            'search': self.request.GET.get('search', ''),
            'marca': self.request.GET.get('marca', ''),
            'cor': self.request.GET.get('cor', ''),
            'condicao': self.request.GET.get('condicao', ''),
            'combustivel': self.request.GET.get('combustivel', ''),
            'transmissao': self.request.GET.get('transmissao', ''),
            'ano_min': self.request.GET.get('ano_min', ''),
            'ano_max': self.request.GET.get('ano_max', ''),
            'preco_min': self.request.GET.get('preco_min', ''),
            'preco_max': self.request.GET.get('preco_max', ''),
            'ordem': self.request.GET.get('ordem', 'recente'),
        }
        
        # Estatísticas para exibição
        total_carros = self.get_queryset().count()
        context['total_carros'] = total_carros
        
        return context
    

class CarroDetailView(DetailView):
    model = Carro
    template_name = 'website/detalhe.html'
    context_object_name = 'carro'
    
    def get_queryset(self):
        """Otimiza a query com relacionamentos necessários"""
        return Carro.objects.select_related(
            'modelo__marca',
            'cor'
        ).prefetch_related(
            'fotos',
            'opcionais'
        )
    
    def get_object(self, queryset=None):
        """Sobrescreve para garantir que apenas carros disponíveis sejam exibidos"""
        if queryset is None:
            queryset = self.get_queryset()
        
        # Busca o carro pelo pk
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        
        try:
            obj = queryset.get()
        except Carro.DoesNotExist:
            raise Http404("Carro não encontrado")
        
        # Verifica se o carro está disponível para visualização
        # (opcional: pode remover se quiser mostrar carros vendidos)
        if not obj.disponivel_venda and not obj.disponivel_aluguel:
            raise Http404("Este veículo não está mais disponível")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carro = self.object
        
        # Fotos organizadas (principal primeiro, depois por ordem)
        fotos = carro.fotos.all().order_by('-foto_principal', 'ordem', 'data_upload')
        context['fotos'] = fotos
        context['foto_principal'] = fotos.filter(foto_principal=True).first() or fotos.first()
        
        # Opcionais organizados por categoria
        opcionais = carro.opcionais.filter(ativo=True).order_by('categoria', 'nome')
        opcionais_por_categoria = {}
        for opcional in opcionais:
            categoria = opcional.categoria or 'Outros'
            if categoria not in opcionais_por_categoria:
                opcionais_por_categoria[categoria] = []
            opcionais_por_categoria[categoria].append(opcional)
        context['opcionais_por_categoria'] = opcionais_por_categoria
        
        # Carros relacionados (mesma marca e categoria, excluindo o atual)
        carros_relacionados = Carro.objects.select_related(
            'modelo__marca', 'cor'
        ).prefetch_related('fotos').filter(
            modelo__marca=carro.modelo.marca,
            modelo__categoria=carro.modelo.categoria,
            disponivel_venda=True
        ).exclude(id=carro.id)[:4]
        context['carros_relacionados'] = carros_relacionados
        
        # Informações técnicas organizadas
        especificacoes = {
            'Ano de Fabricação': carro.ano_fabricacao,
            'Ano do Modelo': carro.ano_modelo,
            'Quilometragem': f"{carro.quilometragem:,} km".replace(',', '.'),
            'Combustível': carro.get_combustivel_display(),
            'Transmissão': carro.get_transmissao_display(),
            'Número de Portas': carro.numero_portas,
            'Motor': carro.motor,
            'Cor': carro.cor.nome,
            'Categoria': carro.modelo.get_categoria_display(),
        }
        
        # Remove campos vazios
        context['especificacoes'] = {k: v for k, v in especificacoes.items() if v}
        
        # Documentação (apenas para administradores - opcional)
        if self.request.user.is_staff:
            documentacao = {
                'Chassi': carro.chassi,
                'Matrícula': carro.matricula,
                'Documento Único': carro.documento_unico,
            }
            context['documentacao'] = {k: v for k, v in documentacao.items() if v}
        
        # Informações de disponibilidade e preços
        context['disponibilidades'] = {
            'venda': carro.disponivel_venda,
            'aluguel': carro.disponivel_aluguel,
            'preco_venda': carro.preco_venda,
            'preco_aluguel': carro.preco_aluguel_diario,
        }
        
        # Meta informações para SEO
        context['meta_title'] = f"{carro.nome_completo} - {carro.get_condicao_display()}"
        context['meta_description'] = (
            f"{carro.nome_completo} {carro.ano_modelo}, "
            f"{carro.quilometragem:,} km, {carro.get_combustivel_display()}, "
            f"{carro.get_transmissao_display()}. "
            f"{'Disponível para venda' if carro.disponivel_venda else ''}"
            f"{' e aluguel' if carro.disponivel_aluguel else ''}."
        ).replace(',', '.')
        
        return context