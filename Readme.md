# Twitter Impact Analysis

This project is all about collecting the responses of a specific tweet. These collected data will be converted into graphs and tables that will be uploaded to a Weights and Biases repository.

## Installation
To install this project you must download the files from the repository. It also requires the following libraries:
```bash
pip install pandas
pip install json
pip install tweepy
pip install stanza
pip install wandb
pip install pandas
pip install matplotlib
pip install seaborn
pip install numpy
```

Lastly, credentials are required to use Tweepy. These credentials will be saved in a file called "api_credentials.py"
```python
consumer_key = "consumer_key"
consumer_secret = "consumer_secret"
token_key = "token_key"
token_secret = "token_secret"
```

##Outputs

The results of the analysis will be stored in a folder called "output". Within this will also require another folder called "Tweets_analysis".

    .
    ├── output                      #Folder neeeded
    │   ├── Tweets_analysis         #Folder neeeded
             ├──username_tweetid_1  #These folders are automatially created for each tweet analyzed.
             ├──username_tweetid_2
             ...
#

To modify the Weights and Biases repository and the output path, the "gen_plots" function of plot.py must be modified.
```python
import wandb
wandb.init(project='Project_name', entity='username',dir='path', name=' '.join('name of the output'))
```


## Usage

To use the application, it must be run and a graphical interface will appear asking for a link to a tweet.

Due to API limitations, if the tweet to be analyzed has> 400 replies, the program may take approximately 4 minutes or more. Some tweets can cause connection problems with the Twitter endpoint, so if an error occurs with a tweet it is best to try it again in 10 minutes or not analyze it.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

