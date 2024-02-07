from celery import shared_task
import gzip
import pickle
from .models import Database
from .serializers import DatabaseSerializer
from django.core.cache import cache


# função para processar os dados do banco de dados e armazenar no cache
@shared_task
def task_process_database():
    
    data = Database.objects.all()
    # serializa os dados
    serializer = DatabaseSerializer(data, many=True)

    # Comprimir os dados
    data_compressed = gzip.compress(pickle.dumps({'database_data': serializer.data}))

    # Armazena os dados comprimidos no cache
    cache.set('database_data_cache_compressed', data_compressed, timeout=None)

    