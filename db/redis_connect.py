import configparser
import redis


config = configparser.ConfigParser()
config.read('db_config.ini')

redis_config = config['db_redis']

host=redis_config['host']

_redis_conn = redis.Redis(host) 

p = _redis_conn.pubsub()
p.subscribe("NewsFeed")

def redis_subscribe(queue: str):
    global _redis_conn
    

def redis_publish():
    global _redis_conn