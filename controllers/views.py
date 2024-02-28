from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *
from .serializers import DatabaseSerializer
from rest_framework.views import APIView
from django.views import View
from babel.numbers import format_currency
from datetime import datetime
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import gzip
import pickle
from .task import task_process_database
from django.db.models import Sum, FloatField, Value
from django.db.models.functions import Cast
from pyspark.sql import SparkSession
import pyspark.pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)



# create a spark session
builder = SparkSession.builder.appName('BigData App')\
    .config('spark.sql.execution.arrow.pyspark.enabled', 'true')\
    .config('spark.driver.extraClassPath', '/home/spark/postgresql-42.7.1.jar')\
    .config('spark.executor.extraClassPath', '/home/spark/postgresql-42.7.1.jar')

spark = builder.getOrCreate()

engine = create_engine('postgresql://postgres:123456789@localhost:5432/postgres')
Session = sessionmaker(bind=engine)


def homepage(request):
    return render(request, 'homepage.html')


def index(request):
    """ Função para exibir a página com as estatísticas do banco de dados"""

    # Recupera apenas a coluna vlr_total_faturamento do banco de dados
    vlr_total_faturamento_values = Database.objects.values_list('vlr_total_faturamento', flat=True)

    # Calcula o valor total do faturamento
    total_faturamento = sum(float(value.replace(',', '.')) if value.replace('-', '').replace('.', '').isdigit() else 0 for value in vlr_total_faturamento_values)
    # Formata o total_faturamento como uma string de moeda
    total_faturamento_formatado = format_currency(total_faturamento, 'BRL', locale='pt_BR')

    # Calcula o número total de clientes únicos
    total_clientes_unicos = Database.objects.values('nome_do_cliente').distinct().count()
    
    # Calcula o número total de pedidos únicos
    total_pedidos_unicos = Database.objects.values('pedido_faturamento').distinct().count()

    # Define a data atual
    data_atual = datetime.now().date()

    # Filtra apenas os registros do dia atual
    database_data = Database.objects.filter(creat_at=data_atual).values('vlr_total_faturamento')

    # Calcula o valor total do faturamento do dia
    total_faturamento_dia = sum(float(item['vlr_total_faturamento']\
                                .replace(',', '.')) if item['vlr_total_faturamento']\
                                .replace('-', '')\
                                .replace('.', '')\
                                .isdigit()\
                                else 0 for item in database_data)

    # Formata o total_faturamento_dia como uma string de moeda
    total_faturamento_dia_formatado = format_currency(total_faturamento_dia, 'BRL', locale='pt_BR')


    # porcentagem entre o valor total de faturamento e o valor já faturado
    # = valor a faturar / faturamento realizado
    faturamento_orçado = float('90000000'.replace('.', '').replace(',', '.')) 
    porcento_a_faturar = (total_faturamento / faturamento_orçado) * 100 

    # formata a porcentagem para exibir no template
    porcento_a_faturar = "{:.4f}".format(porcento_a_faturar)
    
    # Remova o símbolo de porcentagem '%' do valor antes de passá-lo para o template
    porcento_a_faturar = porcento_a_faturar.replace('%', '') 
    

    # Calcula o valor total de receita de mau uso
    # Calcula o valor total de receita de mau uso
    mau_uso = Database.objects.filter(tipo_de_servico='MauUso').values('vlr_total_faturamento')

    # Calcula total MauUso
    total_mau_uso = sum(float(item['vlr_total_faturamento']\
                            .replace(',', '.')) if item['vlr_total_faturamento']\
                            .replace('-', '')\
                            .replace('.', '')\
                            .isdigit()\
                            else 0 for item in mau_uso)
    total_mau_uso = "{:.2f}".format(total_mau_uso)
    

    # Calcula o valor total de receita de locacao
    locacao = Database.objects.filter(tipo_de_servico='Locacao').values('vlr_total_faturamento')

    total_locacao = sum(float(item['vlr_total_faturamento']
                            .replace(',', '.')) if item['vlr_total_faturamento']\
                            .replace('-', '')\
                            .replace('.', '')\
                            .isdigit()\
                            else 0 for item in locacao)
    total_locacao = "{:.2f}".format(total_locacao)
    
 
    # Passa o total_faturamento para o template
    return render(request, 'index.html', {
        'total_faturamento_formatado': total_faturamento_formatado,
        'total_clientes_unicos': total_clientes_unicos,
        'total_pedidos_unicos': total_pedidos_unicos,
        'total_faturamento_dia_formatado': total_faturamento_dia_formatado,
        'total_mau_uso': total_mau_uso,
        'total_locacao': total_locacao,
        'porcento_a_faturar': float(porcento_a_faturar)
        })


# função auxiliar para query_result
def apply_filter(data, filter_criteria):
    filtered_data = []
    for row in data:
        # Suponha que filter_criteria seja um dicionário com o nome da coluna como chave e o valor a ser filtrado como valor
        # Por exemplo, {'column1': 'value1', 'column2': 'value2'}
        match = True
        for column, value in filter_criteria.items():
            if row.get(column) != value:
                match = False
                break
        if match:
            filtered_data.append(row)
    return filtered_data


@cache_page(60 * 1) # Cache 1 minuto
def query_result(request):
    try:
        # Obtenha parâmetros de filtragem da solicitação GET
        filter_criteria = request.GET.get('filter_criteria')
        # Tente obter os dados comprimidos do cache
        cached_data_compressed = cache.get('database_data_cache_compressed')

        if cached_data_compressed is not None:
            cached_data = pickle.loads(gzip.decompress(cached_data_compressed))
            # Se os dados estiverem no cache, aplique a filtragem se houver critérios
            if filter_criteria:
                filtered_data = apply_filter(cached_data, filter_criteria)
                return render(request, 'database_query.html', {'database_data': filtered_data})
            else:
                return render(request, 'database_query.html', cached_data)
        
        # Obtenha os dados do banco de dados
        data = spark.read.format("jdbc")\
            .option("url", "jdbc:postgresql://localhost:5432/postgres")\
            .option("dbtable", "(SELECT * FROM pedidosfaturados ORDER BY creat_at DESC LIMIT 5000) as subquery")\
            .option("user", "postgres")\
            .option("password", "123456789")\
            .load()\
            .select('nome_do_cliente', 'loja_cliente', 'cnpj_do_cliente',
                'cnpj_de_faturamento', 'projeto', 'obra', 'id_equipamento',
                'descricao_do_produto', 'dias_de_locacao', 'valor_unitario',
                'valor_bruto', 'vlr_unitario_faturamento', 'quantidade',
                'vlr_total_faturamento', 'indice_aplicado','contrato_legado',
                'periodo_de_faturamento',
            )
        
        # limite de 1000 registros para evitar sobrecarga
        #data = data.limit(2000)

        # Converta os dados para uma lista de dicionários
        data_list = [row.asDict() for row in data.collect()]

        # Comprimi os dados
        data_compressed = gzip.compress(pickle.dumps({'database_data': data_list}))

        # Armazene os dados no cache 
        cache.set('database_data_cache_compressed', data_compressed, timeout=None)

        # Aplique a filtragem se houver critérios
        if filter_criteria:
            filtered_data = apply_filter(data_list, filter_criteria)
            return render(request, 'database_query.html', {'database_data': filtered_data})
        else:
            return render(request, 'database_query.html', {'database_data': data_list})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        # Trate o erro apropriadamente, como retornar uma resposta de erro ou página de erro
        return HttpResponseServerError("Internal Server Error")
    


# função para a carteira online
""" Aqui retorna as informações da carteira do analista de acordo com o seu login"""
@cache_page(60 * 1) # Cache 1 minuto
def carteiraonline_query_result(request):
    try:
        # Obtenha parâmetros de filtragem da solicitação GET
        filter_criteria = request.GET.get('filter_criteria')
        # Tente obter os dados comprimidos do cache
        cached_data_compressed = cache.get('carteiraonline_cache_compressed')

        if cached_data_compressed is not None:
            cached_data = pickle.loads(gzip.decompress(cached_data_compressed))
            # Se os dados estiverem no cache, aplique a filtragem se houver critérios
            if filter_criteria:
                filtered_data = apply_filter(cached_data, filter_criteria)
                return render(request, 'carteiraonline.html', {'carteira_database_data': filtered_data})
            else:
                return render(request, 'carteiraonline.html', cached_data)
        
        data = spark.read.format("jdbc")\
            .option("url", "jdbc:postgresql://localhost:5432/postgres")\
            .option("dbtable", "(SELECT * FROM carteiraonline GROUP BY codigo_cliente, id ORDER BY MAX(creat_at) as subquery")\
            .option("user", "postgres")\
            .option("password", "123456789")\
            .load()\
            .select('projeto', 'codigo_cliente', 'padronizado', 'inicio_de_faturamento',
                    'limite_para_enviar_relatorio', 'data_limite_para_faturar', 'prazo_faturamento_original',
                    'prazo_faturamento_dias_uteis', 'analista', 'valor_previsto', 'faturamento_anterior',
                    'receita', 'status_do_faturamento', 'status_pedido', 'analise_pedido', 'valor_atual'
            )
        
        # limite de 1000 registros para evitar sobrecarga
        #data = data.limit(2000)

        # Converta os dados para uma lista de dicionários
        data_list = [row.asDict() for row in data.collect()]

        # Comprimi os dados
        data_compressed = gzip.compress(pickle.dumps({'carteira_database_data': data_list}))

        # Armazene os dados no cache 
        cache.set('carteiraonline_cache_compressed', data_compressed, timeout=None)

        # Aplique a filtragem se houver critérios
        if filter_criteria:
            filtered_data = apply_filter(data_list, filter_criteria)
            return render(request, 'carteiraonline.html', {'carteira_database_data': filtered_data})
        else:
            return render(request, 'carteiraonline.html', {'carteira_database_data': data_list})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        # Trate o erro apropriadamente, como retornar uma resposta de erro ou página de erro
        return HttpResponseServerError("Internal Server Error")



""""Incluir novos projetos na carteira online"""
def carteiraonline_incluir(request):
    return render(request, 'carteiraonline_novos_projetos.html')