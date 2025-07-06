from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.website.urls')),
    path('core/', include('apps.core.urls')),
    path('veiculos/', include('apps.veiculos.urls')),
    path('vendas/', include('apps.vendas.urls')),
    path('alugueis/', include('apps.alugueis.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
] 

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)