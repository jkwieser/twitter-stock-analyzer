import producer
import requestor
import threading
import twitter
import twitter_api
import yahoo_api


class ProducerFactory():
    
    TWITTER_TOPIC: str = 'twitter'
    YAHOO_TOPIC: str = 'stock'
    TIMEOUT: int = 10    # in seconds
        
    TWITTER_AUTH: twitter_api.TwitterAuthentication = twitter_api.TwitterAuthentication(
        '---', 
        '---', 
        '---', 
        '---'
    )
    
    # (Producer, Requestor, topic_name, topic_key)
    _registrations: [(producer.Producer, requestor.Requestor, str, str)] = []
    _running = False
        
    
    def __init__(self, host: str, port: int, user_token: str, password_token: str):
        self._host = host
        self._port = port
        self._user_token = user_token
        self._password_token = password_token
        
        
    def start(self):
        if self._running:
            print('The factory is already running.')
            return
        self._running = True
        for i, e in enumerate(self._registrations):
            thread = threading.Thread(target = e[0].start, args = (e[1], e[2], e[3], self.TIMEOUT))
            thread.start()
        print(f'The factory has been started with {len(self._registrations)} producers.')
    
    
    def stop(self):
        for i, e in enumerate(self._registrations):
            e[0].stop()
        self._running = False
        print(f'The factory is terminating {len(self._registrations)} producers.')
        self._registrations.clear()
    
    
    def register_twitter(self, search_word: str):
        req = self._create_twitter_requestor(search_word)
        self._register(req, self.TWITTER_TOPIC, search_word)
        
        
    def register_yahoo(self, stock_name: str):
        req = self._create_yahoo_requestor(stock_name)
        self._register(req, self.YAHOO_TOPIC, stock_name)
    
    
    def _register(self, req: requestor.Requestor, topic_name: str, topic_key: str):
        prod = self._create_producer()
        self._registrations.append((prod, req, topic_name, topic_key))
    
    
    def _create_producer(self) -> producer.Producer:
        return producer.Producer(self._host, self._port, self._user_token, self._password_token)
    
    
    def _create_twitter_requestor(self, search_word: str) -> requestor.Requestor:
        return twitter_api.TwitterAPI(self.TWITTER_AUTH, search_word)
    
    
    def _create_yahoo_requestor(self, stock_name: str) -> requestor.Requestor:
        return yahoo_api.YahooFinanceAPI(stock_name)