#!/usr/bin/env python3

import logging

logging.basicConfig(level=logging.DEBUG)

import json
import os
import requests
import re
import shutil
from tempfile import TemporaryDirectory

import redis

import youtube_dl

from telegram.bot import Bot


TG_TOKEN = os.environ["POSTER_TOKEN"]

red = redis.StrictRedis(host=os.environ["POSTER_REDIS_HOST"])

headers = {'User-Agent': 'ubuntu-server:youtubehaiku-archive:0.0.1 (by /u/pingiun)'}

yt_opts = {
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
}


def main():
    bot = Bot(TG_TOKEN)
    r = requests.get('https://reddit.com/r/youtubehaiku.json', headers=headers)
    for post in r.json()['data']['children']:
        if post['data']['domain'] not in ['youtube.com', 'youtu.be']:
            continue
        if red.sismember('youtubehaikus', post['data']['url']):
            continue
        if post['data']['ups'] < 1000 and (post['data']['subreddit'] == 'meirl' or post['data']['subreddit'] == '4chan'):
            continue
        with TemporaryDirectory() as direc:
            yt_opts['outtmpl'] = os.path.join(direc, 'video.%(ext)s')
            with youtube_dl.YoutubeDL(yt_opts) as ydl:
                ydl.download([post['data']['url']])
            with open(os.path.join(direc, 'video.mp4'), 'rb') as f:
                bot.send_message('@ythaiku', text="*{}*\n[View on YouTube]({})\n"
                                                  "[Discuss on reddit](https://reddit.com{})".format(post['data']['title'],
                                                                                                     post['data']['url'],
                                                                                                     post['data']['permalink']),
                                             parse_mode='markdown')
                bot.send_video('@ythaiku', video=f,
                               caption="{}".format(post['data']['title']))
        
        red.sadd('youtubehaikus', post['data']['url'])


if __name__ == '__main__':
    main()
