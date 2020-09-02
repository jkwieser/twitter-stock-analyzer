# Twitter Rest-API reference: https://developer.twitter.com/en/docs/api-reference-index<br>
# Twitter Python-Module reference: https://python-twitter.readthedocs.io/en/latest/


import requestor
import twitter


class TwitterAuthentication():
    
    consumer_key: str = None
    consumer_secret: str = None
    access_token_key: str = None
    access_token_secret: str = None
    
    
    def __init__(self, consumer_key: str, consumer_secret: str, access_token_key: str, access_token_secret: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class TwitterAPI(requestor.Requestor):
    
    _api: twitter.api.Api = None
    _search_word: str = None
    _last_id: int = -1
    
    
    def __init__(self, authentication: TwitterAuthentication, search_word: str):
        if search_word == None or search_word == '':
            raise ValueError('The "search_word" is not allowed to be empty or None.')
        self._search_word = search_word
        self._api = twitter.Api(
            authentication.consumer_key,
            authentication.consumer_secret,
            authentication.access_token_key,
            authentication.access_token_secret
        )
    
    
    def request_new(self) -> [{}]:
        query = f'q={self._search_word}&src=typed_query&f=live&count=100&result_type=recent&since_id={self._last_id}'
        tweets = self._api.GetSearch(raw_query = query)
        if len(tweets) == 0:
            return None
        timestamp = self.get_time()
        tweet_dict_list = []
        for i, e in enumerate(tweets):
            tweet_dict = self._tweet_to_dict(e, timestamp)
            tweet_dict_list.append(tweet_dict)
        self._last_id = tweet_dict_list[0]['tweet']['id']
        return tweet_dict_list

    
    def _tweet_to_dict(self, tweet: twitter.models.Status, timestamp: str) -> {}:
        return {
            'timestamp': timestamp,
            'tweet': {
                'id': tweet.id,
                'username': tweet.user.screen_name,
                'tweet_timestamp': tweet.created_at,
                'text': tweet.text
            }
        }