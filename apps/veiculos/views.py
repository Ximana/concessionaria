# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DeleteView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from .models import Carro, Marca, Modelo, Cor, Opcional, FotoCarro
from .forms import CarroRegistroForm, MarcaRegistroForm, ModeloRegistroForm, CorRegistroForm
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models

class CarroListView(LoginRequiredMixin, ListView):
    model = Carro
    template_name = 'veiculos/lista.html'
    context_object_name = 'carros'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'modelo__marca', 'cor'
        ).prefetch_related('fotos')
        
        # Filtro de busca
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(modelo__nome__icontains=search_query) |
                Q(modelo__marca__nome__icontains=search_query) |
                Q(chassi__icontains=search_query) |
                Q(matricula__icontains=search_query) |
                Q(cor__nome__icontains=search_query)
            )
        
        # Filtro por marca
        marca_id = self.request.GET.get('marca', '')
        if marca_id:
            queryset = queryset.filter(modelo__marca_id=marca_id)
        
        # Filtro por modelo
        modelo_id = self.request.GET.get('modelo', '')
        if modelo_id:
            queryset = queryset.filter(modelo_id=modelo_id)
        
        # Filtro por condição
        condicao = self.request.GET.get('condicao', '')
        if condicao:
            queryset = queryset.filter(condicao=condicao)
        
        # Filtro por combustível
        combustivel = self.request.GET.get('combustivel', '')
        if combustivel:
            queryset = queryset.filter(combustivel=combustivel)
        
        # Filtro por disponibilidade
        disponibilidade = self.request.GET.get('disponibilidade', '')
        if disponibilidade == 'venda':
            queryset = queryset.filter(disponivel_venda=True)
        elif disponibilidade == 'aluguel':
            queryset = queryset.filter(disponivel_aluguel=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar contexto para filtros
        context['marcas'] = Marca.objects.filter(ativo=True).order_by('nome')
        context['modelos'] = Modelo.objects.filter(ativo=True).select_related('marca').order_by('marca__nome', 'nome')
        context['cores'] = Cor.objects.filter(ativo=True).order_by('nome')
        
        # Choices para filtros
        context['condicao_choices'] = Carro.CONDICAO_CHOICES
        context['combustivel_choices'] = Carro.COMBUSTIVEL_CHOICES
        context['disponibilidade_choices'] = [
            ('', 'Todas'),
            ('venda', 'Disponível para Venda'),
            ('aluguel', 'Disponível para Aluguel'),
        ]
        
        # Preservar parâmetros de filtro e busca
        context['search_query'] = self.request.GET.get('search', '')
        context['marca_selecionada'] = self.request.GET.get('marca', '')
        context['modelo_selecionado'] = self.request.GET.get('modelo', '')
        context['condicao_selecionada'] = self.request.GET.get('condicao', '')
        context['combustivel_selecionado'] = self.request.GET.get('combustivel', '')
        context['disponibilidade_selecionada'] = self.request.GET.get('disponibilidade', '')
        
        # Adicionar formulário para registro de carro
        context['form'] = CarroRegistroForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = CarroRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            # Separar a primeira foto antes de salvar o carro
            primeira_foto = form.cleaned_data.pop('primeira_foto', None)
            
            # Criar o carro
            carro = form.save()
            
            # Se uma foto foi enviada, criar o objeto FotoCarro
            if primeira_foto:
                FotoCarro.objects.create(
                    carro=carro,
                    foto=primeira_foto,
                    foto_principal=True,
                    ordem=1,
                    descricao='Foto principal'
                )
            
            messages.success(request, f'Carro {carro.nome_completo} cadastrado com sucesso!')
            return redirect('administracao:detalhes_veiculo', pk=carro.pk)
            
        # Se o formulário não for válido, retornar à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class CarroDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """View para remover carros"""
    model = Carro
    success_url = reverse_lazy('administracao:lista_veiculos')  # Ajuste conforme seu URL name
    success_message = "Veículo removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        # Pega o objeto antes de deletar para mostrar no success message
        self.object = self.get_object()
        success_message = f"Veículo {self.object.nome_completo} removido com sucesso!"
        
        # Deleta o objeto
        response = super().delete(request, *args, **kwargs)
        
        # Adiciona a mensagem de sucesso
        messages.success(self.request, success_message)
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carro'] = self.object
        return context
    
class CarroDetailView(LoginRequiredMixin, DetailView):
    model = Carro
    template_name = 'veiculos/detalhes.html'
    context_object_name = 'carro'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulário para edição
        context['form'] = CarroRegistroForm(instance=self.object)
        
        # Carrega as fotos do carro ordenadas
        context['fotos'] = self.object.fotos.all().order_by('ordem', 'data_upload')
        
        # Foto principal ou primeira foto
        foto_principal = self.object.fotos.filter(foto_principal=True).first()
        if not foto_principal:
            foto_principal = self.object.fotos.first()
        context['foto_principal'] = foto_principal
        
        # Opcionais do carro
        context['opcionais'] = self.object.opcionais.all()
        
        # Todos os opcionais disponíveis para adicionar
        context['opcionais_disponiveis'] = Opcional.objects.exclude(
            id__in=self.object.opcionais.values_list('id', flat=True)
        ).filter(ativo=True)
        
        # Histórico de alterações (se você tiver um modelo de auditoria)
        # context['historico'] = self.object.historico.all()[:10]
        
        # Informações técnicas organizadas
        context['especificacoes'] = {
            'Motor': self.object.motor or 'Não informado',
            'Combustível': self.object.get_combustivel_display(),
            'Transmissão': self.object.get_transmissao_display(),
            'Número de Portas': self.object.numero_portas or 'Não informado',
            'Quilometragem': f"{self.object.quilometragem:,} km".replace(',', '.'),
            'Chassi': self.object.chassi or 'Não informado',
            'Matrícula': self.object.matricula or 'Não informado',
            'Documento Único': self.object.documento_unico or 'Não informado',
        }
        
        # Status de disponibilidade
        context['disponibilidade'] = {
            'venda': self.object.disponivel_venda,
            'aluguel': self.object.disponivel_aluguel,
        }
        
        # Preços formatados
        context['preco_venda_formatado'] = f"Kz {self.object.preco_venda:,.2f}".replace(',', '.') if self.object.preco_venda else None
        context['preco_aluguel_formatado'] = f"Kz {self.object.preco_aluguel_diario:,.2f}/dia".replace(',', '.') if self.object.preco_aluguel_diario else None
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Atualizar informações do carro
        if 'atualizar_carro' in request.POST:
            form = CarroRegistroForm(request.POST, instance=self.object)
            if form.is_valid():
                form.save()
                messages.success(request, 'Informações do veículo atualizadas com sucesso!')
                return redirect('admninistracao:detalhes_veiculo', pk=self.object.pk)
            else:
                messages.error(request, 'Erro ao atualizar as informações do veículo.')
                return self.get(request, *args, **kwargs)
        
        # Upload de nova foto
        if 'upload_foto' in request.POST:
            foto_file = request.FILES.get('foto')
            descricao = request.POST.get('descricao_foto', '')
            
            if foto_file:
                # Determinar a próxima ordem
                ultima_ordem = self.object.fotos.aggregate(
                    max_ordem=models.Max('ordem')
                )['max_ordem'] or 0
                
                nova_foto = FotoCarro.objects.create(
                    carro=self.object,
                    foto=foto_file,
                    descricao=descricao,
                    ordem=ultima_ordem + 1
                )
                
                # Se é a primeira foto, marcar como principal
                if not self.object.fotos.filter(foto_principal=True).exists():
                    nova_foto.foto_principal = True
                    nova_foto.save()
                
                messages.success(request, 'Foto adicionada com sucesso!')
                return redirect('administracao:detalhes_veiculo', pk=self.object.pk)
            else:
                messages.error(request, 'Selecione uma foto para upload.')
        
        # Remover foto
        if 'remover_foto' in request.POST:
            foto_id = request.POST.get('foto_id')
            try:
                foto = FotoCarro.objects.get(id=foto_id, carro=self.object)
                era_principal = foto.foto_principal
                foto.delete()
                
                # Se era foto principal, definir outra como principal
                if era_principal:
                    primeira_foto = self.object.fotos.first()
                    if primeira_foto:
                        primeira_foto.foto_principal = True
                        primeira_foto.save()
                
                messages.success(request, 'Foto removida com sucesso!')
                return redirect('administracao:detalhes_veiculo', pk=self.object.pk)
            except FotoCarro.DoesNotExist:
                messages.error(request, 'Foto não encontrada.')
        
        # Definir foto principal
        if 'definir_principal' in request.POST:
            foto_id = request.POST.get('foto_id')
            try:
                # Remover foto principal atual
                self.object.fotos.update(foto_principal=False)
                
                # Definir nova foto principal
                foto = FotoCarro.objects.get(id=foto_id, carro=self.object)
                foto.foto_principal = True
                foto.save()
                
                messages.success(request, 'Foto principal definida com sucesso!')
                return redirect('administracao:detalhes_veiculo', pk=self.object.pk)
            except FotoCarro.DoesNotExist:
                messages.error(request, 'Foto não encontrada.')
        
        # Adicionar opcional
        if 'adicionar_opcional' in request.POST:
            opcional_id = request.POST.get('opcional_id')
            try:
                opcional = Opcional.objects.get(id=opcional_id, ativo=True)
                self.object.opcionais.add(opcional)
                messages.success(request, f'Opcional "{opcional.nome}" adicionado com sucesso!')
                return redirect('administracao:detalhes_veiculo', pk=self.object.pk)
            except Opcional.DoesNotExist:
                messages.error(request, 'Opcional não encontrado.')
        
        # Remover opcional
        if 'remover_opcional' in request.POST:
            opcional_id = request.POST.get('opcional_id')
            try:
                opcional = Opcional.objects.get(id=opcional_id)
                self.object.opcionais.remove(opcional)
                messages.success(request, f'Opcional "{opcional.nome}" removido com sucesso!')
                return redirect('administracao:detalhes_veiculo', pk=self.object.pk)
            except Opcional.DoesNotExist:
                messages.error(request, 'Opcional não encontrado.')
        
        return super().get(request, *args, **kwargs)

# View AJAX para atualizar ordem das fotos
def atualizar_ordem_fotos(request, pk):
    """View AJAX para atualizar a ordem das fotos"""
    if request.method == 'POST' and request.is_ajax():
        carro = get_object_or_404(Carro, pk=pk)
        foto_ids = request.POST.getlist('foto_ids[]')
        
        for i, foto_id in enumerate(foto_ids, 1):
            try:
                foto = FotoCarro.objects.get(id=foto_id, carro=carro)
                foto.ordem = i
                foto.save(update_fields=['ordem'])
            except FotoCarro.DoesNotExist:
                continue
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

# MARCAS CORES E MODELOS
class GerenciamentoView(LoginRequiredMixin, ListView):
    """View unificada para gerenciar Marcas, Modelos e Cores"""
    template_name = 'veiculos/gerenciamento.html'
    context_object_name = 'marcas'
    paginate_by = 10

    def get_queryset(self):
        # Por padrão, retorna marcas para a aba principal
        queryset = Marca.objects.all()
        search_query = self.request.GET.get('search_marca', '')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) | 
                Q(pais_origem__icontains=search_query)
            )
        return queryset.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Busca para modelos
        search_modelo = self.request.GET.get('search_modelo', '')
        modelos = Modelo.objects.select_related('marca').all()
        if search_modelo:
            modelos = modelos.filter(
                Q(nome__icontains=search_modelo) |
                Q(marca__nome__icontains=search_modelo) |
                Q(categoria__icontains=search_modelo)
            )
        
        # Busca para cores
        search_cor = self.request.GET.get('search_cor', '')
        cores = Cor.objects.all()
        if search_cor:
            cores = cores.filter(nome__icontains=search_cor)
        
        # Formulários
        context.update({
            'modelos': modelos.order_by('marca__nome', 'nome'),
            'cores': cores.order_by('nome'),
            'form_marca': MarcaRegistroForm(),
            'form_modelo': ModeloRegistroForm(),
            'form_cor': CorRegistroForm(),
            'search_marca': self.request.GET.get('search_marca', ''),
            'search_modelo': search_modelo,
            'search_cor': search_cor,
            'tab_ativa': self.request.GET.get('tab', 'marcas'),
            'estatisticas': self.get_estatisticas(),
        })
        
        return context

    def get_estatisticas(self):
        """Retorna estatísticas dos dados"""
        return {
            'total_marcas': Marca.objects.count(),
            'marcas_ativas': Marca.objects.filter(ativo=True).count(),
            'total_modelos': Modelo.objects.count(),
            'modelos_ativos': Modelo.objects.filter(ativo=True).count(),
            'total_cores': Cor.objects.count(),
            'cores_ativas': Cor.objects.filter(ativo=True).count(),
        }

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        tab_redirect = request.POST.get('tab', 'marcas')
        
        if action == 'add_marca':
            return self.handle_add_marca(request, tab_redirect)
        elif action == 'add_modelo':
            return self.handle_add_modelo(request, tab_redirect)
        elif action == 'add_cor':
            return self.handle_add_cor(request, tab_redirect)
        
        # Se chegou aqui, retorna para a view normal
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def handle_add_marca(self, request, tab_redirect):
        form = MarcaRegistroForm(request.POST)
        if form.is_valid():
            marca = form.save()
            messages.success(request, f'Marca "{marca.nome}" cadastrada com sucesso!')
            return redirect(f'{request.path}?tab={tab_redirect}')
        else:
            messages.error(request, 'Erro ao cadastrar marca. Verifique os dados informados.')
            self.object_list = self.get_queryset()
            context = self.get_context_data(form_marca=form)
            context['tab_ativa'] = tab_redirect
            return self.render_to_response(context)

    def handle_add_modelo(self, request, tab_redirect):
        form = ModeloRegistroForm(request.POST)
        if form.is_valid():
            modelo = form.save()
            messages.success(request, f'Modelo "{modelo.nome}" cadastrado com sucesso!')
            return redirect(f'{request.path}?tab={tab_redirect}')
        else:
            messages.error(request, 'Erro ao cadastrar modelo. Verifique os dados informados.')
            self.object_list = self.get_queryset()
            context = self.get_context_data(form_modelo=form)
            context['tab_ativa'] = tab_redirect
            return self.render_to_response(context)

    def handle_add_cor(self, request, tab_redirect):
        form = CorRegistroForm(request.POST)
        if form.is_valid():
            cor = form.save()
            messages.success(request, f'Cor "{cor.nome}" cadastrada com sucesso!')
            return redirect(f'{request.path}?tab={tab_redirect}')
        else:
            messages.error(request, 'Erro ao cadastrar cor. Verifique os dados informados.')
            self.object_list = self.get_queryset()
            context = self.get_context_data(form_cor=form)
            context['tab_ativa'] = tab_redirect
            return self.render_to_response(context)


def deletar_marca(request, pk):
    """View para deletar marca"""
    if request.method == 'POST':
        marca = get_object_or_404(Marca, pk=pk)
        nome_marca = marca.nome
        try:
            marca.delete()
            messages.success(request, f'Marca "{nome_marca}" removida com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao remover marca: {str(e)}')
    
    return redirect('administracao:gerenciamento')


def deletar_modelo(request, pk):
    """View para deletar modelo"""
    if request.method == 'POST':
        modelo = get_object_or_404(Modelo, pk=pk)
        nome_modelo = modelo.nome
        try:
            modelo.delete()
            messages.success(request, f'Modelo "{nome_modelo}" removido com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao remover modelo: {str(e)}')
    
    return redirect('administracao:gerenciamento?tab=modelos')


def deletar_cor(request, pk):
    """View para deletar cor"""
    if request.method == 'POST':
        cor = get_object_or_404(Cor, pk=pk)
        nome_cor = cor.nome
        try:
            cor.delete()
            messages.success(request, f'Cor "{nome_cor}" removida com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao remover cor: {str(e)}')
    
    return redirect('administracao:gerenciamento?tab=cores')


def obter_modelos_por_marca(request):
    """View AJAX para obter modelos de uma marca específica"""
    marca_id = request.GET.get('marca_id')
    if marca_id:
        modelos = Modelo.objects.filter(marca_id=marca_id, ativo=True).values('id', 'nome')
        return JsonResponse({'modelos': list(modelos)})
    return JsonResponse({'modelos': []})