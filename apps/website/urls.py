#apps/core/urls-py
from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
   # path('', views.home_view, name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('contato/', views.contacto_view, name='contato'),
    path('login/', views.login_website_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    
    path('', views.HomeView.as_view(), name='home'),
    
    path('loja/', views.CarroListView.as_view(), name='loja'),
    path('carro/<int:pk>/', views.CarroDetailView.as_view(), name='carro_detailhe'),
]

    
  