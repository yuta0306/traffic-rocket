from flask import Flask
from flask import render_template, redirect, request, url_for, jsonify
import requests
from requests_oauthlib import OAuth1Session

import os
import sys
import json
import re

from crawl import Crawler
from database import insert_user, update_user, is_exist, delete_user
from tweets import parser
from auto_deploy import git_flow

CK = os.environ.get('CK')
CS = os.environ.get('CS')

app = Flask(__name__)
user = None
pages = []
excludes = []

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global user
    user = OAuth1Session(CK, CS)
    params = {
        'oauth_callback': 'https://traffic-rocket.herokuapp.com/oauth'
    }
    res = user.post('https://api.twitter.com/oauth/request_token', params)
    params = parser(res.text)

    user = OAuth1Session(CK, CS, params['oauth_token'], params['oauth_token_secret'])
    redirect_url = 'https://api.twitter.com/oauth/authorize?oauth_token={}'.format(params['oauth_token'])

    return redirect(redirect_url)

@app.route('/oauth')
def oauth():
    global user
    url = request.url
    print(url)
    text = re.sub('.*\?', '', url)
    params = parser(text)
    user = OAuth1Session(CK, CS, params['oauth_token'], params['oauth_verifier'])
    res = user.post('https://api.twitter.com/oauth/access_token', params)
    params = parser(res.text)
    print(params)
    AK, AS = params['oauth_token'], params['oauth_token_secret']
    id_ = params['user_id']

    user = OAuth1Session(CK, CS, AK, AS)
    
    with open('datas.json', 'r') as f:
        obj = json.load(f)

    if is_exist(id_):
        print('update')
        update_user(id_, AK, AS)
    else:
        print('insert')
        insert_user(id_, AK, AS)

    return redirect(url_for('application'))

@app.route('/get_id')
def get_id():
    global user
    params = {
        'count': 1,
    }
    res = user.get('https://api.twitter.com/1.1/statuses/user_timeline.json', params=params)
    user_data = json.loads(res.text)
    id_ = user_data[0]['user']['id_str']

    with open('datas.json', 'r') as f:
        datas = json.load(f)

    if id_ in datas.keys():
        url = datas[id_]
    else:
        url = []

    obj = {
        'id': id_,
        'url': url,
    }
    obj = json.dumps(obj)

    return jsonify(obj)


@app.route('/application')
def application():
    return render_template('app.html')

@app.route('/crawl/<base>')
def crawl(base: str):
    clr = Crawler(base)
    pages = clr.crawl(depth=0)
    pages = {
        'urls': pages,
    }
    results = json.dumps(pages)

    return jsonify(results)

@app.route('/update', methods=['POST'])
def update():
    id_ = request.json['id']
    url = request.json['url']

    with open('datas.json', 'r') as f:
        datas = json.load(f)

    if id_ in datas.keys():
        if not url in datas[id_]:
            datas[id_].append(url)
            msg = '記事の追加に成功しました!!'
        else:
            msg = '{}はすでに登録されています。'.format(url)
        obj = {
            'id': id_,
            'url': datas[id_],
            'msg': msg,
        }
        
    else:
        obj = {
            'id': id_,
            'url': [url],
            'msg': '記事の追加に成功しました!!'
        }
        datas[id_] = [url]
    obj = json.dumps(obj)

    with open('datas.json', 'w') as f:
        json.dump(datas, f)

    return jsonify(obj)

@app.route('/remove', methods=['POST'])
def remove():
    id_ = request.json['id']
    url = request.json['url']

    with open('datas.json', 'r') as f:
        datas = json.load(f)

    urls = list(filter(lambda x: x != url, datas[id_]))
    datas[id_] = urls
    
    with open('datas.json', 'w') as f:
        json.dump(datas, f)

    obj = {
        'id': id_,
        'url': urls,
        'msg': '{}を削除しました。'.format(url),
    }

    obj = json.dumps(obj)

    return jsonify(obj)

@app.route('/delete', methods=['POST'])
def delete_user():
    id_ = request.json['id']

    delete(id_)
    with open('datas.json', 'r') as f:
        obj = json.load(f)
    
    del obj[id_]
    with open('datas.json', 'w') as f:
        json.dump(obj, f)

    empty = json.dumps({})

    return jsonify(empty)

@app.route('/save')
def save():
    name = os.environ.get('GITHUB_NAME')
    email = os.environ.get('GITHUB_EMAIL')
    username = os.environ.get('GITHUB_USERNAME')
    password = os.environ.get('GITHUB_PASSWORD')
    git_flow('traffic-rocket.git', username, password, name, email, 'master')

    empty = json.dumps({})

    return jsonify(empty)
    

if __name__ == "__main__":
    app = app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))