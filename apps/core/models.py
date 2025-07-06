from django.db import models

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
        db_table = 'configuracao'
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'
        ordering = ['chave']
        db_table = 'configuracoes'

    def __str__(self):
        return f'{self.chave}: {self.valor}'

    def save(self, *args, **kwargs):
        """Override do save para garantir que a data_atualizacao seja atualizada"""
        super().save(*args, **kwargs)