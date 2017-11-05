FROM python:3-stretch-onbuild

RUN apt-get update && apt-get install ffmpeg -y

CMD [ "python", "./bot.py" ]
