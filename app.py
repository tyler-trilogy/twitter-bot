import matplotlib
matplotlib.use('Agg')

import tweepy
import spacy
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint
import time

import os
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

#######################################################################
# setup
#######################################################################

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# Load model
import en_core_web_md
nlp = en_core_web_md.load()

me = 'TylerUCSD'

#######################################################################
# functions
#######################################################################

def build_analysis(user):

    # Create dictionary to hold text and label entities
    tweet_dict = {'text': [], 'label': []}


    # Loop throught tweets
    for tweet in api.user_timeline(user):

        # Use nlp on each tweet
        doc = nlp(tweet['text'])

        # Print the entities for each doc
        for ent in doc.ents:
            tweet_dict['text'].append(ent.text)
            tweet_dict['label'].append(ent.label_)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(tweet_dict)
    df.head()

    # Group by labels
    label_freq = df.groupby(['label']).count()
    label_freq.plot.bar()
    
    plt.savefig('chart.png')
    
    api.update_with_media('chart.png', f'Tweet labels for @{user}')


def find_all_requests():
    requests = set()

    for tweet in api.search(f'@{me} Analyze:')['statuses']:
        for user_mention in tweet['entities']['user_mentions']:
            if user_mention['screen_name'] != me:
                requests.add(user_mention['screen_name'])

    return requests


def find_completed_requests():
    completed_requests = set()
    
    for tweet in api.user_timeline(rpp=100):
        if 'labels for' not in tweet['text']:
            continue
        for user_mention in tweet['entities']['user_mentions']:
            if user_mention['screen_name'] != me:
                completed_requests.add(user_mention['screen_name'])
                
    return completed_requests


def find_next_request():
    all_requests = find_all_requests()
    completed_requests = find_completed_requests()
    new_requests = all_requests - completed_requests
    
    try:
        return new_requests.pop()
    except:
        return None
    

#######################################################################
# execution loop
#######################################################################

while True:
    print('Updating Twitter')

    next_request = find_next_request()
    print('Next Request:', next_request)
    
    if next_request:
        build_analysis(next_request)
    
    time.sleep(20)

