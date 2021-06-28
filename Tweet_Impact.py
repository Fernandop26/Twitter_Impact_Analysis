import csv
import base64
import os
import time
import PySimpleGUI as sg
import requests
# import UI_Twitte_Impact as twui
import tweepy
import pandas as pd
from opts import parse_args
from plot import gen_plots
from scrap import user_info, user_info_v2, get_author_info
import api_credentials
import pandas._libs.tslibs.base

auth = tweepy.OAuthHandler(api_credentials.consumer_key, api_credentials.consumer_secret)
auth.set_access_token(api_credentials.token_key, api_credentials.token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_tweet(id_of_tweet):
    tweet = api.show_status(id=id_of_tweet)


def get_replies(username='Ne0nImpala', tweet_id='1379772379023486977'):
    name = username
    target_tweet_id = tweet_id
    replies = []
    # for tweet in tweepy.Cursor(api.search, q='to:' + name, result_type='recent', timeout=999999).items(470):
    for tweet in tweepy.Cursor(api.search, q='to:' + name, since_id=tweet_id, tweet_mode='extended').items():
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str == target_tweet_id):
                replies.append(tweet)

    return replies


def tweetstoDataFrame_v2(tweets):
    url = ["https://twitter.com/", "/status/"]
    tweets_list = []
    for tweet in tweets:
        text = tweet.full_text.split()
        for word in text:
            if word.startswith("http"):
                text.remove(word)
        tweet.text = ' '.join(text[1:])
        info = [tweet.id, tweet.id_str,
                str(tweet.created_at.year) + '-' + str(tweet.created_at.month) + '-' + str(tweet.created_at.day),
                str(tweet.created_at.hour) + ':' + str(tweet.created_at.minute) + ':' + str(tweet.created_at.second)
            , tweet.author.id, tweet.author.screen_name
            , tweet.author.name, None if tweet.author.location == None or "" else tweet.author.location, tweet.text,
                tweet.lang, tweet.entities['user_mentions'],
                tweet.entities['urls'],
                tweet.entities['media'][0]['media_url'] if len(tweet.entities) >= 5 else None,
                tweet.author.verified,
                0,
                tweet.retweet_count,
                tweet.favorite_count,
                tweet.entities['hashtags'], 0,
                url[0] + tweet.author.screen_name + url[1] + str(tweet.id),
                tweet.author.followers_count,
                tweet.author.profile_image_url,
                int(tweet.favorite_count) + int(tweet.retweet_count) + int(tweet.author.followers_count)]
        tweets_list.append(info)
    df = pd.DataFrame(tweets_list,
                      columns=["id", "id_str", "date", "time", "user_id", "username", "name", "place", "tweet",
                               "language", "mentions",
                               "urls", "photos", "verified", "replies_count", "retweets_count", "likes_count",
                               "hashtags", "retweet", "reply_link", "followers_count", "profile_image", "reach_count"])
    return df


def tweetstoDataFrame(tweets):
    url = ["https://twitter.com/", "/status/"]
    tweets_list = []
    for tweet in tweets:
        text = tweet.text.split()
        for word in text:
            if word.startswith("http"):
                text.remove(word)
        tweet.text = ' '.join(text[1:])
        info = [tweet.id, tweet.id_str,
                str(tweet.created_at.year) + '-' + str(tweet.created_at.month) + '-' + str(tweet.created_at.day),
                str(tweet.created_at.hour) + ':' + str(tweet.created_at.minute) + ':' + str(tweet.created_at.second)
            , tweet.author.id, tweet.author.screen_name
            , tweet.author.name, None if tweet.author.location == None or "" else tweet.author.location, tweet.text,
                tweet.lang, tweet.entities['user_mentions'],
                tweet.entities['urls'],
                tweet.entities['media'][0]['media_url'] if len(tweet.entities) >= 5 else None,
                tweet.author.verified,
                0,
                tweet.retweet_count,
                tweet.favorite_count,
                tweet.entities['hashtags'], 0,
                url[0] + tweet.author.screen_name + url[1] + str(tweet.id),
                tweet.author.followers_count,
                tweet.author.profile_image_url,
                int(tweet.favorite_count) + int(tweet.retweet_count) + int(tweet.author.followers_count)]
        tweets_list.append(info)
    df = pd.DataFrame(tweets_list,
                      columns=["id", "id_str", "date", "time", "user_id", "username", "name", "place", "tweet",
                               "language", "mentions",
                               "urls", "photos", "verified", "replies_count", "retweets_count", "likes_count",
                               "hashtags", "retweet", "reply_link", "followers_count", "profile_image", "reach_count"])
    return df


def main(url):
    print("Getting User informacion...")
    url_split = url.split('/')
    username = url_split[-3]
    tweet_id = url_split[-1]

    output = "output\\Tweets_analysis\\" + username + "_" + tweet_id

    os.makedirs(output, exist_ok=True)
    # Pass the tweets list to the above function to create a DataFrame

    # Get data from the tweet
    tweet = api.get_status(tweet_id)
    try:
        language = tweet.lang
        if language != 'es' or language != 'eng':
            language = 'es'
    except:
        language = 'es'

    print("Getting replies...")
    # get the tweet reply's data
    try:
        replies = get_replies(username, tweet_id)
        DataSet = tweetstoDataFrame_v2(replies)

        # Export the dataset to csv
        DataSet.to_csv(output + '\\tweets.csv')
        author_info = get_author_info(username, output)
        user_info(DataSet, output)
        user_info_v2(DataSet, output)
        print("Plotting Data...")
        # gen_plots(output, args.keyword)
        gen_plots(output, username, author_info, tweet, language)
    except:
        UI_Tweepy_Error()


def UI_Tweepy_Error():
    layout = [
        [[sg.Text('Sorry! Connection to the Twitter Endpoint has not been successfully created. Try another Tweet.'),
          sg.Text(""), sg.Text(size=(15, 1), key='-Warning')]],
        [[sg.Button("Close", key="Exit")]]
    ]
    window = sg.Window("Tweet Impact", layout)
    event, values = window.read()
    while True:
        if event == "Exit" or event == sg.WIN_CLOSED:
            break


def UI_Tweepy_Success():
    layout = [
        [[sg.Text('The connection was successful!'), sg.Text(""), sg.Text(size=(15, 1), key='-Warning')]],
        [[sg.Button("Close", key="Exit")]]
    ]
    window = sg.Window("Tweet Impact", layout)
    event, values = window.read()
    while True:
        if event == "Exit" or event == sg.WIN_CLOSED:
            break


def UI_Tweet_impact():
    layout = [
        [[sg.Text('Welcome to Tweet Impact Software!'), sg.Text(""), sg.Text(size=(15, 1), key='-Warning')]],
        [sg.Text('Input a Tweet Link to get data from it: '), sg.InputText(key='-IN')],
        [[sg.Button("Search", key="open"), sg.Button("Close", key="Exit")]]
    ]
    window = sg.Window("Tweet Impact", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "open":
            try:
                HEADERS = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                }
                # html = requests.get("https://twitter.com/NintendoUK/status/1386953264055218177",timeout=5, headers=HEADERS)
                requests.get(values['-IN'], timeout=5, headers=HEADERS)
                window.close()
                # loading_screen()
                # print(values['-IN'])
                try:
                    main(values['-IN'])
                except:
                    pass
                UI_Tweepy_Success()
                break
            except:
                window['-Warning'].update("URL not valid!")
        if event == "loading":
            pass
            # loading_sus_screen()
    window.close()


if __name__ == '__main__':
    while True:
        try:
            UI_Tweet_impact()
            break
        except tweepy.TweepError:
            UI_Tweepy_Error()
            print("Connection error! Trying in 30 seconds")
            time.sleep(30)
