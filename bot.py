from database import fetch_all_users
from tweets import gen_tweet, post_tweet

import json
import random
import os

CK = os.environ.get('CK')
CS = os.environ.get('CS')

if __name__ == "__main__":
    users = fetch_all_users()
    with open('datas.json', 'r') as f:
        datas = json.load(f)
    for user in users:
        id_, AK, AS = user
        print(id_, AK, AS)
        urls = datas[id_]
        url = urls[random.randint(0, len(urls)-1)]
        tweet = gen_tweet(url)
        result = post_tweet(CK, CS, AK, AS, tweet)
        print(json.loads(result.text))
        print('====================')