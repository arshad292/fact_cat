from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import  logging
from celery import shared_task
import random
import redis

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@shared_task
def fetch_cat_facts():
    try:
        response = requests.get("https://cat-fact.herokuapp.com/facts")
        if response.status_code == 200:
            data = response.json()
            # Store fetched cat facts in Redis
            for fact in data['all']:
                fact_id = fact['_id']
                fact_text = fact['text']
                redis_client.set(f"cat_fact_{fact_id}", fact_text)
            return True
        else:
            logger.error(f"Failed to fetch cat facts. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"An error occurred while fetching cat facts: {e}")
        return False
    
# Create your views here.


@api_view(['GET'])
def health_check(request):
    return Response({'status':'ok'}, status=200)

@api_view(['POST'])
def fetch_fact(request):
    fetch_cat_facts.delay()
    return Response({'success':True})

@api_view(['GET'])
def get_fact(request):
    """
    Endpoint to retrieve a random cat fact from Redis.
    """
    cat_fact_keys = redis_client.keys('cat_fact_*')  
    if cat_fact_keys:
        random_fact_key = random.choice(cat_fact_keys)
        cat_fact = redis_client.get(random_fact_key).decode('utf-8')  
    else:
        return Response({'error': 'no_cat_facts_available'}, status=404)