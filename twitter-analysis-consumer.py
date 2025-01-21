import uuid
import _thread
import json
import pytz
from datetime import datetime
from dateutil import tz
from confluent_kafka import Consumer
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter
import time as time
import numpy as np
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer



def update_ui(some=0):
    plt.gca().clear()
    threshold = 0
    np_tweet_counts_tsla = np.asarray(list_tweet_counts_tsla, dtype=np.float32)
    np_stock_prices_tsla = np.asarray(list_stock_prices_tsla, dtype=np.float32)
    np_tweet_counts_ms = np.asarray(list_tweet_counts_ms, dtype=np.float32)
    np_stock_prices_ms = np.asarray(list_stock_prices_ms, dtype=np.float32)

    np_sent_tsla = np.asarray(list_sentiments_tsla, dtype=np.float32)
    np_sent_ms = np.asarray(list_sentiments_ms, dtype=np.float32)

    axs[0, 0].plot(range(1,len(np_stock_prices_ms)+1), np_stock_prices_ms, 'xkcd:blue')
    axs[0, 0].set_title('Microsoft Stock Price $',fontsize=10)
    axs[0, 1].plot(range(1,len(np_stock_prices_tsla)+1), np_stock_prices_tsla, 'xkcd:blue')
    axs[0, 1].set_title('Tesla Stock Price $',fontsize=10)
    axs[1, 0].plot(range(1,len(np_stock_prices_ms)+1), np_tweet_counts_ms, 'xkcd:blue')
    red_patch = mpatches.Patch(color='xkcd:red', label='Negative comments') # legend
    green_patch = mpatches.Patch(color='xkcd:green', label='Positive comments') # legend
    blue_patch = mpatches.Patch(color='xkcd:blue', label='Neutral comments') # legend
    axs[1, 0].legend(handles=[red_patch, green_patch,blue_patch],loc='best', prop={'size': 5}) # legend

    axs[1, 0].fill_between(range(1,len(list_sentiments_ms)+1),[i/max(np_tweet_counts_ms)+0.03 for i in np_tweet_counts_ms],where=np_sent_ms > threshold,
                color='xkcd:green', alpha=0.9, transform=axs[1, 0].get_xaxis_transform())  
    axs[1, 0].fill_between(range(1,len(list_sentiments_ms)+1), [i/max(np_tweet_counts_ms)+0.03 for i in np_tweet_counts_ms], where=np_sent_ms < threshold,
                color='xkcd:red', alpha=0.9, transform=axs[1, 0].get_xaxis_transform())  
    axs[1, 0].fill_between(range(1,len(list_sentiments_ms)+1), [i/max(np_tweet_counts_ms)+0.03 for i in np_tweet_counts_ms], where=np_sent_ms == threshold,
                color='xkcd:blue', alpha=0.9, transform=axs[1, 0].get_xaxis_transform())             
    axs[1, 0].set_title('Tweets with word "Gates" / count',fontsize=10)
    axs[1, 1].plot(range(1,len(np_stock_prices_tsla)+1), np_tweet_counts_tsla, 'xkcd:blue')

    red_patch = mpatches.Patch(color='xkcd:red', label='Negative comments') # legend
    green_patch = mpatches.Patch(color='xkcd:green', label='Positive comments') # legend
    aqua_patch = mpatches.Patch(color='xkcd:blue', label='Neutral comments') # legend
    axs[1, 1].legend(handles=[red_patch, green_patch,aqua_patch],loc='best', prop={'size': 5}) # legend

    axs[1, 1].fill_between(range(1,len(np_tweet_counts_tsla)+1),[i/max(np_tweet_counts_tsla)+0.03 for i in np_tweet_counts_tsla], where=np_sent_tsla > threshold,
                color='xkcd:green', alpha=0.9, transform=axs[1, 1].get_xaxis_transform())  
    axs[1, 1].fill_between(range(1,len(np_tweet_counts_tsla)+1),[i/max(np_tweet_counts_tsla)+0.03 for i in np_tweet_counts_tsla], where=np_sent_tsla < threshold,
                color='xkcd:red', alpha=0.9, transform=axs[1, 1].get_xaxis_transform()) 
    axs[1, 1].fill_between(range(1,len(np_tweet_counts_tsla)+1),[i/max(np_tweet_counts_tsla)+0.03 for i in np_tweet_counts_tsla], where=np_sent_tsla == threshold,
                color='xkcd:blue', alpha=0.9, transform=axs[1, 1].get_xaxis_transform())   
    axs[1, 1].set_title('Tweets with word "Musk" / count',fontsize=10)

    for ax in axs.flat:
        ax.set(xlabel='Updates over Time')
        ax.xaxis.label.set_size(7)
        ax.yaxis.label.set_size(7)
        ax.xaxis.set_tick_params(labelsize=6)
        ax.yaxis.set_tick_params(labelsize=6)
        
    # Hide x labels and tick labels for top plots and y ticks for right plots.

    fig.tight_layout(pad=1.0)

    # updating the UI dynamically
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            return

# create consumer and establish connection
c = Consumer({
    'bootstrap.servers': '*******.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '-fill in -',
    'sasl.password': '- fill in-',
    'group.id': str(uuid.uuid1()),  # this will create a new consumer group on each invocation.
    'auto.offset.reset': 'earliest'
})

twitter_searchword_ms = "gates"
twitter_searchword_tsla = "musk"
stock_ms = "MSFT"
stock_tsla = "TSLA"


list_tweets_tsla = []
list_tweets_ms = []


list_sentiments_ms = []
list_sentiments_tsla = []

list_tweet_counts_tsla = []
list_tweet_counts_ms = []

list_stock_prices_tsla = []
list_stock_prices_ms = []

count_tweets_tsla = 0
count_tweets_ms = 0

#sentinent analyzer
sid = SentimentIntensityAnalyzer()

# setup the plotting
plt.ion()
# set up the figure
fig, axs = plt.subplots(2, 2)
plt.show(block=False)

# subscribe to both topics
c.subscribe(['twitter', 'stock'])


# Create a separate thread for the UI

update_ui()



# message receiving start
try:
    while True:  
        msg = c.poll(0.1)  # Wait for 0.1 secs for message
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to `session.timeout.ms` for
            #   the group to rebalance and start consuming.
            continue
        if msg.error():
            # Errors are typically temporary, print error and continue.
            print("Consumer error: {}".format(msg.error()))
            continue


        if msg.topic() == 'twitter':

            if str(msg.key(), 'utf-8').lower() == twitter_searchword_tsla.lower():
                myjson = json.loads(str(msg.value(), 'utf-8'))
                list_tweets_tsla.append(myjson['tweet']['text'])
                count_tweets_tsla +=1 
            
            if str(msg.key(), 'utf-8').lower() == twitter_searchword_ms.lower():
                myjson = json.loads(str(msg.value(), 'utf-8'))
                list_tweets_ms.append(myjson['tweet']['text'])
                count_tweets_ms +=1  
                
            if count_tweets_tsla < 1:
                if str(msg.key(), 'utf-8').lower() == twitter_searchword_tsla.lower():
                    count_tweets_tsla +=1 
                else:
                    count_tweets_ms +=1
                continue
                

        if msg.topic() == 'stock':

            if str(msg.key(), 'utf-8').lower() == stock_tsla.lower():
                list_tweet_counts_tsla.append(count_tweets_tsla)
                count_tweets_tsla = 0
                myjson = json.loads(str(msg.value(), 'utf-8'))
                list_stock_prices_tsla.append(myjson['value'])
                
                if len(list_tweets_tsla) > 0:
                    temp = []
                    for tweet in list_tweets_tsla:
                        temp.append(sid.polarity_scores(tweet)['compound'])
                    list_sentiments_tsla.append(sum(temp) / len(temp))
                    list_tweets_tsla = []
                else:
                    list_sentiments_tsla.append(0)
                
                update_ui()

            if str(msg.key(), 'utf-8').lower() == stock_ms.lower():
                list_tweet_counts_ms.append(count_tweets_ms)
                count_tweets_ms = 0
                myjson = json.loads(str(msg.value(), 'utf-8'))
                list_stock_prices_ms.append(myjson['value'])

                
                if len(list_tweets_ms) > 0:
                    temp = []
                    for tweet in list_tweets_ms:
                        temp.append(sid.polarity_scores(tweet)['compound'])
                    list_sentiments_ms.append(sum(temp) / len(temp))
                    list_tweets_ms = []
                else:
                    list_sentiments_ms.append(0)
                
                update_ui()
                

        
        print("TSLA")
        print(list_tweet_counts_tsla)
        print(list_stock_prices_tsla)
        print(list_sentiments_tsla)
        
        print("MSFT")
        print(list_tweet_counts_ms)
        print(list_stock_prices_ms)
        print(list_sentiments_ms)

              

except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    print("consuming is over")
