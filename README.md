# YouTube Haiku Telegram Bot

This bot is designed to repeatedly poll /r/youtubehaiku and mirror the youtube posts on Telegram. I have a bot running on a gcloud kubernetes cluster that posts to t.me/ythaiku.

# How to run this in a docker container

This repo includes a Dockerfile for a python:3-onbuild with Debian stretch. I had trouble converting to mp4 (which Telegram requires) with avconv, and I didn't want to go through the trouble of installing ffmpeg on Debian Jessie.
As there is no official python 3 onbuild stretch image, I created one myself.

You have to build this image first before you build the bot image. This is really easy:

`docker build -t python:3-stretch-onbuild 3-stretch-onbuild`

Now you can build the bot image:

`docker build -t youtubehaikubot .`

To run this image you must supply a bot token and redis host to use as environment variables, for example:

```bash
docker run -d --name some-redis redis
docker run --rm -it -e POSTER_TOKEN=yourtelegramtoken -e POSTER_REDIS_HOST=redis --link some-redis:redis youtubehaikubot
```

The bot will pull the top posts from /r/youtubehaiku and post them to @ythaiku, but your bot probably doesn't have permission to post there. You should change `bot.py` in some places:

- Change the `headers` variable to include your User-Agent and your username.
- Change the `@ythaiku` in `send_message` and `send_video` to a channel which your bot is allowed to post to.

# How to run this on kubernetes

I'm using Google Cloud for my kubernetes cluster, but this should be able to run on any kubernetes cluster. I have included some yaml files in this repo to setup your cluster.

First of all you should run a redis service. `redis.yaml` is everything you should need. It includes a Deployment, Service, and PersistentVolumeClaim. Run `kubectl create -f redis.yaml` to deploy.

To test the bot once (using a Job), run `kubectl create -f run.yaml`. This file and `schedule.yaml` assume that your redis service has the `redis` hostname. If this is not the case, change the POSTER_REDIS_HOST value in the yaml. Your Telegram token should be in a kubernetes secreet, the yaml files assume that it is stored in the `telegram-poster` secret with key `token`.

If `run.yaml` is working correctly, you can create a kubernetes cronjob with `schedule.yaml`. By default this checks every 8 minutes, but you can change the cron line using standard cron syntax. Keep in mind that you may need to change some values here too if you changed them in `run.yaml`.
