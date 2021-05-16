from bs4 import BeautifulSoup
import requests
from requests_oauthlib import OAuth1Session

import datetime

def _fetch_source(url: str) -> BeautifulSoup:
    res = requests.get(url)
    source = BeautifulSoup(res.content, 'html5lib')
    
    return source

def _parse_desc(source: BeautifulSoup) -> str:
    metas = source.find_all('meta')
    desc = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs.keys() and meta.attrs['name'] == 'og:description'] or None
    if desc:
        desc = desc[0]
    else:
        desc = source.find('title').text or None
        if not desc:
            desc = source.find('h1').text or None
        
    return desc

def gen_tweet(url: str) -> str:
    source = _fetch_source(url)
    content = _parse_desc(source)

    max_ = 140 - (len(url) + 15)
    if len(content) > max_:
        tweet = content[:max_] + '...\n' + datetime.datetime.now().strftime('%Y/%m/%d') + '\n' + url
    else:
        tweet = content + '\n\n' + url

    return tweet

def post_tweet(CK, CS, AK, AS, text):
    URL = 'https://api.twitter.com/1.1/statuses/update.json'
    tw = OAuth1Session(CK, CS, AK, AS)
    params = {
        'status': text,
    }
    result = tw.post(URL, params)

    return result

def parser(text: str):
    comb = text.split('&')
    parameters = dict()

    for param in comb:
        param_list = param.split('=')
        parameters[param_list[0]] = param_list[1]

    return parameters
