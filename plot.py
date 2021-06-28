import csv
import os
import re
import string
import stanza
import wandb
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from opts import parse_args
matplotlib.use('agg')
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def set_html_style():
    with open('Tables_style', 'r', encoding='utf-8') as myfile:
        style = myfile.read()
    return style

def plot_top(tweets, path):

    top_users = tweets['username'].value_counts()[:20]
    top_likes = []
    top_retweets = []
    top_replies = []

    for user in top_users.keys():

        top_likes.append(tweets[tweets["username"] == user]["likes_count"].sum())
        top_retweets.append(tweets[tweets["username"] == user]["retweets_count"].sum())
        top_replies.append(tweets[tweets["username"] == user]["replies_count"].sum())

    data = pd.DataFrame.from_dict({"Usuario": list(top_users.keys()), "Tweets": top_users.values, "Likes": top_likes, "Retweets": top_retweets, "Respuestas": top_replies})

    fig = plt.figure()
    ax = fig.add_subplot(2, 2, 1)
    b = sns.barplot("Tweets", "Usuario", data=data, ax=ax)
    b.tick_params(labelsize=12)
    ax.set_ylabel('')
    ax.set_xlabel('Tweets', fontsize=15)
    ax = fig.add_subplot(2, 2, 2)
    b = sns.barplot("Likes", "Usuario", data=data, ax=ax)
    b.tick_params(labelsize=12)
    ax.set_ylabel('')
    ax.set_xlabel('Likes', fontsize=15)
    ax = fig.add_subplot(2, 2, 3)
    b = sns.barplot("Respuestas", "Usuario", data=data, ax=ax)
    b.tick_params(labelsize=12)
    ax.set_ylabel('')
    ax.set_xlabel('Respuestas', fontsize=15)
    ax = fig.add_subplot(2, 2, 4)
    b = sns.barplot("Retweets", "Usuario", data=data, ax=ax)
    b.tick_params(labelsize=12)
    ax.set_ylabel('')
    ax.set_xlabel('Retweets', fontsize=15)
    fig.text(0.04, 0.5, 'Usuario', va='center', rotation='vertical', fontsize=20)
    fig.set_size_inches(32, 18)
    plt.savefig(path + "/top_data.png", bbox_inches='tight')
    wandb.log({"Usuarios Relevantes": wandb.Image(plt)})
    plt.close(fig)

def author_info(author, style):


    # html_author = author.to_html()
    html_author = "{1}{0}".format(author.to_html(index=False, justify="center"), style)
    wandb.log({"Datos del Autor": wandb.Html(html_author, inject=False)})


def plot_evolution(tweets, keyword, path):

    tweets['date'] = pd.to_datetime(tweets['date'])
    tweets.sort_values(by='date')['date'].value_counts().plot(fontsize=15)
    matplotlib.rcParams.update({'font.size': 10})
    plt.ylabel("Numero de Tweets", fontsize=15)
    plt.xlabel("Fecha", fontsize=15)
    fig = plt.gcf()
    fig.set_size_inches(32, 18)
    plt.legend(keyword)
    plt.savefig(path + "/tweet_evolution.png", bbox_inches='tight')
    wandb.log({"Evolucion Tweet": wandb.Image(plt)})
    plt.close(fig)


def plot_activity(data, path):

    data = data[data["time"] != "Unknown"]

    b = sns.distplot(data['time'].apply(lambda x: int(x.split(':')[0])), bins=24, norm_hist=False,kde=False)
    b.set_xlabel("Hora del Dia", fontsize=15)
    b.set_ylabel("Numero de Tweets", fontsize=15)
    b.tick_params(labelsize=10)
    b.set_xticks(list(range(0, 24)))
    fig = plt.gcf()
    fig.set_size_inches(32, 18)
    plt.savefig(path + "/tweet_activity.png", bbox_inches='tight')
    wandb.log({"Actividad Usuarios": wandb.Image(plt)})
    plt.close(fig)


def plot_user_loc(users, path):
    loc = {}
    for v in users.values():
        if v["location"] in loc:
            loc[v["location"]] += 1
        else:
            loc[v["location"]] = 1


    # del loc["Unkown"]
    fig1, ax1 = plt.subplots()
    total = sum([*loc.values()])
    if total != 0:
        # plt.pie(loc.values(), startangle=90, labels=loc.keys(), autopct=lambda pct: f"{pct:.1f}%\n({int(pct/100. * total) + 1:d})")
        plt.pie(loc.values(), startangle=90, labels=loc.keys(), autopct=lambda pct: f"{pct:.1f}%\n({int(pct/100. * total) :d})")
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")

        fig = plt.gcf()

        fig.gca().add_artist(centre_circle)
        ax1.axis("equal")
        plt.tight_layout()
        fig.set_size_inches(32, 18)
        plt.savefig(path + "/user_location.png", bbox_inches='tight')
        wandb.log({"Ubicacion del Usuario": wandb.Image(plt)})
        plt.close(fig1)
        plt.close(fig)


def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?¿\]\%', ' ', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”…«»]', '', text)
    text = re.sub('\n', ' ', text)
    return text

def tweet_reach(tweets, users, author, tweet, style):
    verified = 0
    # reach = author.followers_count
    reach = int(author['followers'][0])

    for v in users.values():
        verified += v["verified"]

    p_verified = (verified / len(users)) * 100
    # number of followers (who has less) * numbers of rt of the twees + likes + followers of user
    try:
        min_reach = reach + tweets['followers_count'].min() * tweet.retweet_count + tweet.favorite_count
    except:
        min_reach=tweet.retweet_count + tweet.favorite_count
    # number of average followers * numbers of rt of the twees + likes + followers of user
    try:
        max_reach = reach + int(tweets['followers_count'].mean()) * tweet.retweet_count + tweet.favorite_count
    except:
        max_reach = tweet.retweet_count + tweet.favorite_count
    reach_table = pd.DataFrame({"Numero de Respuestas": len(tweets), "Usuarios Verificados (%)": p_verified, "Personas alcanzadas (min)": min_reach, "Personas alcanzadas (max)":max_reach},
                        index=[0])
    # html_reach = reach_table.to_html()
    html_string = "{1}{0}".format(reach_table.to_html(index=False, justify="center"), style)
    wandb.log({"Tweet Reach": wandb.Html(html_string, inject=False)})



def store_info(tweets, path, language, style):
    nltk.download('stopwords')
    nltk.download('punkt')
    if language == "en":
        language = 'english'
    elif language == "es":
        language = "spanish"
    else:
        language = "spanish"

    stop_words = set(stopwords.words(language))
    # with open('table_style.txt', 'r', encoding='utf-8') as myfile:
    #     style = myfile.read()

    tweets.dropna(subset=["likes_count", "retweets_count"], inplace=True)
    tweets["likes_count"][tweets["likes_count"] == "Unknown"] = 0
    tweets["retweets_count"][tweets["retweets_count"] == "Unknown"] = 0

    top_likes = tweets.sort_values(by="likes_count", ascending=False)[:100]
    top_replies = tweets.sort_values(by="replies_count", ascending=False)[:100]
    top_retweets = tweets.sort_values(by="retweets_count", ascending=False)[:100]
    info = pd.concat([top_likes, top_retweets, top_replies])[["tweet", "likes_count", "replies_count", "retweets_count"]]
    info.rename(columns={'tweet': 'Tweet', 'likes_count': 'Likes', "replies_count": "Respuestas", "retweets_count": "Retweets"}, inplace=True)
    info.rename(columns={'tweet': 'Tweet', 'likes_count': 'Likes', "retweets_count": "Retweets"}, inplace=True)
    info.drop_duplicates(inplace=True)
    info['Tweet']=info['Tweet'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    #### Save Text ###
    tweet_anls=[]
    nlp = stanza.Pipeline(lang=language, processors='tokenize,pos,lemma,depparse')
    tweets_words={}
    real_words={}
    for tweet in info['Tweet']:
        tweet = clean_text(tweet)
        """ Clean Words """
        word_tokens = word_tokenize(tweet)
        filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
        filtered_sentence = []
        for w in word_tokens:
            if w not in stop_words:
                filtered_sentence.append(w)
        tw = nlp(tweet)
        for sentence in tw.sentences:
            for dep_edge in sentence.dependencies:
                if dep_edge[1] =='amod':
                    tweet_anls.append(dep_edge[0].text +" "+dep_edge[2].text)
                if dep_edge[2].text in tweets_words:
                    tweets_words[dep_edge[2].text]+=dep_edge[0].id
                else:
                    tweets_words[dep_edge[2].text] = dep_edge[0].id
        for single_word in filtered_sentence:
            if single_word in real_words:
                real_words[single_word] += real_words[single_word]
            else:
                real_words[single_word] = 1

    df_meanings = pd.DataFrame(tweet_anls, columns=['Valoracion'])
    df_meanings.drop_duplicates(inplace=True)
    # html_meanings = df_meanings.to_html()
    html_meanings = "{1}{0}".format(df_meanings.to_html(index=False, justify="center"), style)
    wandb.log({"Valoraciones": wandb.Html(html_meanings, inject=False)})

    # for dep_edge in self.dependencies:
    #     print((dep_edge[2].text, dep_edge[0].id, dep_edge[1]), file=file)
    tweets_words=dict(sorted(tweets_words.items(), reverse=True, key=lambda item: item[1]))
    df_words = pd.DataFrame(list(tweets_words.items()), columns=['Palabras', 'Cantidad'])

    ##Real words
    tweets_real_words = dict(sorted(real_words.items(), reverse=True, key=lambda item: item[1]))
    df_r_words = pd.DataFrame(list(tweets_real_words.items()), columns=['Palabras', 'Cantidad'])

    df_words = df_words.iloc[:100]
    # html_words = df_words.to_html()
    html_words = "{1}{0}".format(df_r_words.to_html(index=False, justify="center"), style)
    wandb.log({"Top Words": wandb.Html(html_words, inject=False)})
    ##Real words
    # html_r_words = df_r_words.to_html()
    html_r_words= "{1}{0}".format(df_r_words.to_html(index=False, justify="center"), style)
    wandb.log({"Top Real Words": wandb.Html(html_r_words, inject=False)})


    info.to_csv(os.path.join(path, "top_tweets.csv"), index=False)
    html_string = "{1}{0}".format(info.to_html(index=False, justify="center"), style)
    wandb.log({"Top Tweets": wandb.Html(html_string, inject=False)})


def gen_plots(path, keyword, author, tweet, language):
    stanza.download(language)
    wandb.init(project='Tweet_Impact', entity='fernandop26',dir=path, name=' '.join(keyword))
    sns.set(style="whitegrid")
    style = set_html_style()

    tweets = pd.read_csv(os.path.join(path, "tweets.csv"))
    tweets.drop_duplicates(inplace=True)
    tweets.replace(np.nan, "Unknown", inplace=True)

    users = json.load(open(os.path.join(path, "users.json"), "r", encoding='utf-8'))


    # User info
    author_info(author, style)
    tweet_reach(tweets, users, author, tweet, style)
    plot_user_loc(users, path)
    store_info(tweets, path, language, style)

    # Trend Info
    plot_evolution(tweets, keyword, path)
    plot_top(tweets, path)
    plot_activity(tweets, path)


if __name__ == "__main__":
    args = parse_args()
    path = os.path.join(args.root, '_'.join(args.keyword))
    gen_plots(path, args.keyword)