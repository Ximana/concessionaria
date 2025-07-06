from django.urls import path
from . import views

app_name = 'administracao'

urlpatterns = [
    # Lista e cadastro de carros
    path('', views.CarroListView.as_view(), name='lista_veiculos'),
     path('remover/<int:pk>/', views.CarroDeleteView.as_view(), name='remover_veiculo'),
     path('carro/detalhe/<int:pk>/', views.CarroDetailView.as_view(), name='detalhes_veiculo'),
    
    # Página principal de gerenciamento
    path('gerenciamento/', views.GerenciamentoView.as_view(), name='gerenciamento'),
    
    # URLs para deletar
    path('marca/deletar/<int:pk>/', views.deletar_marca, name='deletar_marca'),
    path('modelo/deletar/<int:pk>/', views.deletar_modelo, name='deletar_modelo'),
    path('cor/deletar/<int:pk>/', views.deletar_cor, name='deletar_cor'),
    
    # AJAX
    path('ajax/modelos-por-marca/', views.obter_modelos_por_marca, name='obter_modelos_por_marca'),
    
    # Manter as URLs antigas para compatibilidade
    path('marcas/', views.GerenciamentoView.as_view(), {'tab': 'marcas'}, name='marca_lista'),
    path('marca/remover/<int:pk>/', views.deletar_marca, name='marca_remover'),
]
