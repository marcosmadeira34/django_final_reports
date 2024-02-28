from django.db import models
from django.contrib.auth.models import User

# classe para o banco de dados

class Database(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE,
     #                        null=True, default='',
     #                        verbose_name='criado pelo usuário:')
    
    id = models.IntegerField(primary_key=True)
    creat_at = models.DateField(auto_now_add=True)
    #updatAt = models.DateField(auto_now=True)
    codigo_cliente = models.CharField(null=True, default='-')
    loja_cliente = models.CharField(null=True, default='-')
    nome_do_cliente = models.CharField(null=True, default='-')
    cnpj_do_cliente = models.CharField(null=True, default='-')
    cnpj_de_faturamento = models.CharField(null=True, default='-')
    cnpj_de_remessa = models.CharField(null=True, default='-')
    equipamento = models.CharField(null=True, default='-')
    nota_de_remessa = models.CharField(null=True, default='-')
    data_de_remessa = models.DateField(null=True, default=None)
    serie_da_nf_remessa = models.CharField(null=True, default='-')
    produto = models.CharField(null=True, default='-')
    descricao_do_produto = models.CharField(null=True, default='-')
    quantidade = models.CharField(null=True, default='-')
    projeto = models.CharField(null=True, default='-')
    obra = models.CharField(null=True, default='-')
    prazo_do_contrato = models.CharField(null=True, default='-')
    data_de_ativacao_legado = models.DateField(null=True, default=None)
    data_de_ativacao = models.DateField(null=True, default=None)
    ultimo_faturamento = models.DateField(null=True, default=None)
    data_do_termo = models.DateField(null=True, default=None)
    aniversario = models.DateField(null=True, default=None)
    desc_ajuste = models.CharField(null=True, default='-')
    indice_aplicado = models.CharField(null=True, default='-')
    dias_de_locacao = models.CharField(null=True, default='-')
    valor_de_origem = models.CharField(null=True, default='-')
    valor_unitario = models.CharField(null=True, default='-')
    valor_bruto = models.CharField(null=True, default='-')
    tipo_do_mes = models.CharField(null=True, default='-')
    contrato_legado = models.CharField(null=True, default='-')
    acrescimo = models.CharField(null=True, default='-')
    franquia = models.CharField(null=True, default='-')
    id_equipamento = models.CharField(null=True, default='-')
    id_equip_substituido = models.CharField(null=True, default='-')
    data_da_substituicao = models.DateField(null=True, default=None)
    data_proximo_faturamento = models.DateField(null=True, default=None)
    data_fim_locacao = models.DateField(null=True, default=None)
    tipo_de_servico = models.CharField(null=True, default='-')
    email = models.CharField(null=True, default='-')
    calculo_reajuste = models.CharField(null=True, default='-')
    nome_da_obra = models.CharField(null=True, default='-')
    numero_da_as = models.CharField(null=True, default='-')
    pedido_faturamento = models.CharField(null=True, default='-')
    nf_de_faturamento = models.CharField(null=True, default='-')
    serie_de_faturamento = models.CharField(null=True, default='-')
    data_de_faturamento = models.DateField(null=True, default=None)
    qtde_faturamento = models.CharField(null=True, default='-')
    vlr_unitario_faturamento = models.CharField(null=True, default='-')
    vlr_total_faturamento = models.CharField(null=True, default='-')
    periodo_de_faturamento = models.CharField(null=True, default='-')
    status_de_cobranca = models.CharField(null=True, default='-')
    natureza = models.CharField(null=True, default='-')

   
    
    class Meta:
        db_table = 'pedidosfaturados'
        managed = False



# models para carteira online:
class CarteiraModels:
    creat_at = models.DateField(auto_now_add=True)
    projeto = models.CharField(null=False, default='-')
    codigo_cliente = models.CharField(null=False, default='-')
    padronizado = models.CharField(null=False, default='-')
    inicio_de_faturamento = models.IntegerField(null=False, default='-')
    limite_para_enviar_relatorio = models.IntegerField(null=False, default='-')
    data_limite_para_faturar = models.IntegerField(null=False, default='-')
    prazo_faturamento_original = models.DateField(null=False, default='-')
    prazo_faturamento_dias_uteis = models.DateField(null=False, default='-')
    analista = models.CharField(null=False, default='-')
    valor_previsto = models.FloatField(null=False, default='-')
    faturamento_anterior = models.FloatField(null=False, default='-')
    receita = models.CharField(null=False, default='-')
    status_do_faturamento = models.CharField(null=False, default='-')
    status_pedido = models.CharField(null=False, default='-')
    analise_pedido = models.CharField(null=False, default='-')
    valor_atual = models.FloatField(null=False, default='-')




    
    class Meta:
        db_table = 'carteiraonline'
        managed = False



    
