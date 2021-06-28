import pandas as pd
import os
import json
import datetime
import tweepy
import api_credentials
import stanza


auth = tweepy.OAuthHandler(api_credentials.consumer_key, api_credentials.consumer_secret)
auth.set_access_token(api_credentials.token_key, api_credentials.token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



def user_info(tweets, path):
    tweets = tweets.sort_values(by="retweets_count", ascending=False)[:100]
    users = tweets["username"].apply(lambda x: x.replace("@", "")).values.tolist()

    user_impact = {}
    tweet_reach = {}

    user_metas = api.lookup_users(screen_names=users)

    for user_meta in user_metas:
        following = []
        user_impact[user_meta.screen_name] = {"following": following,
                                              "n_tweets": user_meta.statuses_count,
                                              "location": user_meta.location if user_meta.location != '' else "Unkown",
                                              "n_followers": user_meta.followers_count,
                                              "likes": user_meta.favourites_count,
                                              "verified": int(user_meta.verified)}

    with open(os.path.join(path, "users.json"), "w", encoding="utf-8") as f:
        json.dump(user_impact, f)


def user_info_v2(tweets, path):
    tweets = tweets.sort_values(by="reach_count", ascending=False)[:int(len(tweets) * 0.2)]
    users_info = tweets[
        ['username', 'name', 'place', 'language', 'photos', 'verified', 'likes_count', 'retweets_count', 'hashtags',
         'profile_image', 'reach_count']].copy()

    out = users_info.to_json(orient='records')[1:-1].replace('},{', '} {')
    with open(os.path.join(path, 'users_info.json'), 'w', encoding="utf-8") as f:
        f.write(out)


def get_author_info(author_username, path):
    user = api.get_user(author_username)
    list_author_info = [user.id, user.screen_name, user.name.encode("ascii", "ignore"), user.description.encode("ascii", "ignore"), user.followers_count,
                        user.profile_image_url]
    list_author_info_df = pd.DataFrame([list_author_info],
                                       columns=["id", "screen name", "name", "description", "followers", "profile_img"])
    out = list_author_info_df.to_json(orient='records')[1:-1].replace('},{', '} {')
    with open(os.path.join(path, 'author_info.json'), 'w', encoding="utf-8") as f:
        f.write(out)
    return list_author_info_df
