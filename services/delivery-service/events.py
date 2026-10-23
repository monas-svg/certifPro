import json, os, logging, threading, time
import pika

RABBIT_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
EXCHANGE = "certifpro"
RETRY_DELAY = 5


def _params():
    params = pika.URLParameters(RABBIT_URL)
    params.heartbeat = 30
    params.blocked_connection_timeout = 60
    return params


def publish(routing_key, payload, retries=3):
    for attempt in range(1, retries + 1):
        try:
            conn = pika.BlockingConnection(_params())
            try:
                ch = conn.channel()
                ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
                ch.basic_publish(exchange=EXCHANGE, routing_key=routing_key,
                                 body=json.dumps(payload).encode(),
                                 properties=pika.BasicProperties(delivery_mode=2))
            finally:
                conn.close()
            return True
        except Exception:
            logging.exception("publish failed %s (tentative %s/%s)", routing_key, attempt, retries)
            time.sleep(1)
    return False


def subscribe(routing_key, queue, handler):
    def run():
        while True:
            conn = None
            try:
                conn = pika.BlockingConnection(_params())
                ch = conn.channel()
                ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
                ch.queue_declare(queue=queue, durable=True)
                ch.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=routing_key)
                ch.basic_qos(prefetch_count=1)

                def cb(ch_, method, props, body):
                    try:
                        handler(json.loads(body))
                        ch_.basic_ack(method.delivery_tag)
                    except Exception:
                        logging.exception("handler failed %s", routing_key)
                        ch_.basic_nack(method.delivery_tag, requeue=False)

                ch.basic_consume(queue=queue, on_message_callback=cb)
                logging.info("Consommateur connecté: %s <- %s", queue, routing_key)
                ch.start_consuming()
            except Exception:
                logging.exception("RabbitMQ indisponible, nouvelle tentative dans %ss", RETRY_DELAY)
            finally:
                try:
                    if conn and conn.is_open:
                        conn.close()
                except Exception:
                    pass
            time.sleep(RETRY_DELAY)

    threading.Thread(target=run, daemon=True).start()
