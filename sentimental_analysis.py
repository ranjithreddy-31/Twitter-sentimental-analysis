from tweepy.streaming import StreamListener
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import twitter_credentials as tc
'''Twitter Client'''
class TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth=TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client=API(self.auth)
        self.twitter_user=twitter_user
    def get_twitter_client_api(self):
        return self.twitter_client
    def get_user_timeline_tweets(self,num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    def get_friend_list(self,num_friends):
        friend_list=[]
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).item(num_friends):
            friend_list.append(friend)
        return friend_list
    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets=[]
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets
'''Twitter Authenticator'''
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth=OAuthHandler(tc.CONSUMER_KEY,tc.CONSUMER_SECRET)
        auth.set_access_token(tc.ACCESS_TOKEN,tc.ACCESS_TOKEN_SECRET)
        return auth
class TwitterStreamer():
    """ class for streaming and processing tweets"""
    def __init__(self):
        self.twitter_authenticator=TwitterAuthenticator()
    def stream_tweets(self,filename,hash_tag_list):
        listener=TwitterListener(filename)
        auth=self.twitter_authenticator.authenticate_twitter_app()
        stream=Stream(auth,listener)
        stream.filter(track=hash_tag_list)

class TwitterListener(StreamListener):
    """'basic class that prints recieved tweets to console"""
    def __init__(self,filename):
        self.filename=filename
    def on_data(self,data):
        try:
            print(data)  
            with open(self.filename,'a')as tf:
                tf.write(data)
        except BaseException as e:
            print(str(e))
        return True
    def on_error(self,status):
        if status==420:#Returning False on_data method in case rate limit occurs
            return False
        print(status)
class TweetAnalyzer():
    '''Analyses and categorizes tweets'''
    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())#converting tweets into plain text
    def analyze_sentiment(self,tweet):
        analysis=TextBlob(self.clean_tweet(tweet))#Text Blob is an inbuilt function that analyzes the tweets 
        if analysis.sentiment.polarity>0:
            return 1#positive
        elif analysis.sentiment.polarity==0:
            return 0#neutral
        else:
            return -1#negative

    def tweets_to_dataframe(self,tweets):
        df=pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['Tweets'])
        df['id']=np.array([tweet.id for tweet in tweets])
        df['len']=np.array([len(tweet.text) for tweet in tweets])
        df['date']=np.array([tweet.created_at for tweet in tweets])
        df['source']=np.array([tweet.source for tweet in tweets])
        df['likes']=np.array([tweet.favorite_count for tweet in tweets])
        df['retweets']=np.array([tweet.retweet_count for tweet in tweets])
        
        return df
if __name__=="__main__":
    twitter_client=TwitterClient()
    tweet_analyzer=TweetAnalyzer()
    api=twitter_client.get_twitter_client_api()
    tweets=api.user_timeline(screen_name='@twitter',count=2000)#screen_name=any twitter handle,count=Number of tweets
    df=tweet_analyzer.tweets_to_dataframe(tweets)
    df['sentiment']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['weets']])
    print(df.head)
    time_likes=pd.Series(data=df['likes'].values,index=df['date'])
    time_likes.plot(figsize=(16,4),color='r',label='likes',legend=True)
    time_retweets=pd.Series(data=df['retweets'].values,index=df['date'])
    time_retweets.plot(figsize=(16,4),color='b',label='retweets',legend=True)
    plt.show()