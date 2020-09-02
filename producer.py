import confluent_kafka as kafka
import json
import requestor
import time
import twitter_api
import yahoo_api


class Producer():
    
    _producer: kafka.Producer = None
    _topic_name: str = None
    _topic_key: str = None
    _running = False
    
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self._producer = kafka.Producer({
            'bootstrap.servers': f'{host}:{port}',
            'sasl.username': username,
            'sasl.password': password,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
        })
    
    
    def start(self, requestor: requestor.Requestor, topic_name: str, topic_key: str, timeout: int):
        if timeout < 0:
            raise ValueError('The timeout cannot be negative.')
        # Skip the first. This is  just used for the proper initialization of the requestors' state.
        requestor.request_new()
        print(f'Requestor has been started for the topic "{topic_name}", with the key "{topic_key}".')
        self._running = True
        while self._running:
            data = requestor.request_new()
            if data is not None:
                for i, e in enumerate(data):
                    json_data = json.dumps(e)
                    self._producer.produce(topic_name, key = topic_key, value = json_data, on_delivery = self._callback)
            self._producer.poll(0)
            time.sleep(timeout)
        print(f'Requestor has been stopped for the topic "{topic_name}", with the key "{topic_key}".')
            
            
    def _callback(self, err: kafka.error.ProduceError, msg: kafka.Message):
        if err is not None:
            print(f'Failed to deliver message due to: {err.str()}')
        else:
            print(f'Message ~ Topic: {msg.topic()} ~ Partition: {msg.partition()} ~ Offset: {msg.offset()}')

            
    def stop(self):
        self._running = False