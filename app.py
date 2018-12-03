import matplotlib
matplotlib.use('Agg')

import tweepy
import spacy
import pandas as pd
import matplotlib.pyplot as plt
import time

import en_core_web_sm
nlp = en_core_web_sm.load()

import os
consumer_key = os.environ.get("consumer_key")
consumer_secret = os.environ.get("consumer_secret")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")


# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# Settings
me = 'TylerUCSD'


def post_analysis(username):

    # Create dictionary to hold text and label entities
    tweet_dict = {"text": [], "label": []}

    # Get tweets from a users timeline
    user_tweets = api.user_timeline(username)

    # Loop throught tweets
    for tweet in user_tweets:    
        doc = nlp(tweet["text"])
        if doc.ents:
            for ent in doc.ents:
                tweet_dict["text"].append(ent.text)
                tweet_dict["label"].append(ent.label_)

    # Convert dictionary to DataFrame
    tweet_df = pd.DataFrame(tweet_dict)
    tweet_df.head()
    
    # Group by labels
    label_frequency = tweet_df.groupby(['label']).count()

    # Show bar chart
    label_frequency.plot.bar()    

    # Save bar chart to png
    plt.savefig('chart.png')
    
    # Get bar graph as a figure and tweet chart
    api.update_with_media('chart.png', f'Tweet labels for @{username}')


def find_completed_requests():
    tweets = api.user_timeline(rpp=1000)

    completed_requests = set()
    for tweet in tweets:
        if 'labels for' not in tweet['text']:
            continue        
        for user_mention in tweet['entities']['user_mentions']:
            if user_mention['screen_name'] != me:
                completed_requests.add(user_mention['screen_name'])
                
    return completed_requests


def find_next_request():
    tweets = api.search(f'@{me} Analyze:')['statuses']
    
    requests = set()
    for tweet in tweets:
        for user_mention in tweet['entities']['user_mentions']:
            if user_mention['screen_name'] != me:
                requests.add(user_mention['screen_name'])
        
    new_requests = requests - find_completed_requests()
    
    try:
        return new_requests.pop()
    except:
        return None
    

while True:
    print("Updating Twitter")

    next_request = find_next_request()
    print('Next Request:', next_request)
    
    if next_request:
        post_analysis(next_request)
    
    time.sleep(20)
