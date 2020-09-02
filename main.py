import producer
import producer_factory
import requestor
import twitter_api
import yahoo_api


HOST: str = 'confluent-cloud-host'
PORT: int = 9092
USER_TOKEN: str = 'confluent-cloud-user-token'
PASSWORD_TOKEN: str = 'confluent-cloud-password-token'


factory = producer_factory.ProducerFactory(HOST, PORT, USER_TOKEN, PASSWORD_TOKEN)

factory.register_twitter('Musk')
factory.register_twitter('Gates')
factory.register_yahoo('TSLA')
factory.register_yahoo('MSFT')

factory.start()

# factory.stop()