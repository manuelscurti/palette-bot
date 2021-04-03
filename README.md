# Palette Bot
A Telegram bot which extracts the main color components from pictures

Reach the bot here! [@PaletteMakerBot](https://t.me/PaletteMakerBot)

## About the bot

Telegram bots applications are web servers that listen to updates and send messages through Telegram Bot APIs. This bot is developed in Python3 (using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library) and hosted on Heroku with free-plan service.   

## Local Development

For starting your local instance of the bot, you will need a Telegram Bot token, that you can obtain by talking to @BotFather 

Once you have a token and you cloned the repository, you can start the bot as follows:

```
$ export BOT_TOKEN=YOUR_BOT_TOKEN_HERE
$ python src/bot.py
```

Now you can start chatting with your local instance of the bot, by talking to the bot created by you using BotFather.

## Deploy

This bot has an automatic Continuous Integration pipeline in place. Once a commit is pushed on the main branch, the deployment of the new version of the bot will start.

For the purpouse of deployment, these 3 files are host-specific files:

```
requirements.txt
Aptfile
Procfile
```

Feel free to delete them if you deploy the app on another service.