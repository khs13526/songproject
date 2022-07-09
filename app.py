import json

from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.i3cxp.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.test

import requests
from bs4 import BeautifulSoup

def objectIdDecoder(list):
    for document in list:
        document['_id'] = str(document['_id'])


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/song", methods=["get"])
def song_get():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.genie.co.kr/chart/top200?ditc=M&rtm=N&ymd=20210701', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    songs = soup.select('#body-content > div.newest-list > div > table > tbody > tr')

    song_list = []

    for song in songs:
        title = song.select_one('td.info > a.title.ellipsis').text.strip()
        if "19" in title:
            title = song.select_one('td.info > a.title.ellipsis').text.strip().strip('19금').strip()
        rank = song.select_one('td.number').text[0:2].strip()
        artist = song.select_one('td.info > a.artist.ellipsis').text
        image = song.select_one('td:nth-child(3) > a > img').attrs['src']
        doc = {
            'title': title,
            'rank': rank,
            'artist': artist,
            'image': image
        }
        song_list.append(doc)

    return jsonify({'songs': song_list})

@app.route("/song", methods=["POST"])
def song_post():
    songs = request.get_json('result_give')
    lists = songs['result_give']
    for item in lists:
        db.songs.insert_one(item)
    song_list = list(db.songs.find({}))
    objectIdDecoder(song_list)
    return jsonify({'songs': song_list})

@app.route("/song/delete", methods=["POST"])
def song_delete():
    songs = request.get_json('result_give')
    lists = songs['result_give']
    for item in lists:
        db.songs.delete_one({'_id': ObjectId(item['_id'])})
    return jsonify({'msg': '삭제완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)