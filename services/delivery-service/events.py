import json, os, logging, threading
import pika

RABBIT_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
EXCHANGE = "certifpro"

def publish(routing_key, payload):
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        ch = conn.channel()
        ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        ch.basic_publish(exchange=EXCHANGE, routing_key=routing_key,
                         body=json.dumps(payload).encode(),
                         properties=pika.BasicProperties(delivery_mode=2))
        conn.close()
    except Exception:
        logging.exception("publish failed %s", routing_key)

def subscribe(routing_key, queue, handler):
    def run():
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        ch = conn.channel()
        ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        ch.queue_declare(queue=queue, durable=True)
        ch.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=routing_key)
        ch.basic_qos(prefetch_count=1)
        def cb(ch_, method, props, body):
            try:
                handler(json.loads(body)); ch_.basic_ack(method.delivery_tag)
            except Exception:
                logging.exception("handler failed %s", routing_key)
                ch_.basic_nack(method.delivery_tag, requeue=False)
        ch.basic_consume(queue=queue, on_message_callback=cb)
        ch.start_consuming()
    threading.Thread(target=run, daemon=True).start()
