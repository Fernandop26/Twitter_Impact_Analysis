import argparse
from datetime import date


def parse_args():

    parser = argparse.ArgumentParser("Twint Scrapper")
    parser.add_argument("--keyword", type=str, nargs='*', default="pineapples ", help="keyword to search for")
    parser.add_argument("--root", type=str, default="data")
    parser.add_argument("--since", type=str, default="2011-01-01")
    parser.add_argument("--until", type=str, default=date.today().strftime("%Y-%m-%d"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--username", type=str, default=None)
    parser.add_argument("--tweet_id", type=str, default=None)

    return parser.parse_args()
