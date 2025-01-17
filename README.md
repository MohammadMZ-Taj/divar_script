# Divar Script
A simple python script which collects house information (in [Shiraz](https://en.wikipedia.org/wiki/Shiraz)) from [divar](divar.ir) and sends result to telegram.

# Technologies and Frameworks
sqlalchemy, BeautifulSoap4, postgresql, flask and pyrogram (telegram bot)

# Requirements
The Project requires these packages:
```
beautifulsoup4==4.12.2
Flask==2.3.2
Pyrogram~=2.0.106
PySocks==1.7.1
requests==2.31.0
SQLAlchemy==2.0.19
...
```
and some others.

Install all python packages from requirements.txt:
```
pip install -r requirements.txt
```
## Database configurations
You also need to have [Postgresql](https://www.postgresql.org/) on your system. Create `local_settings.py` in the root of project and add your database configuration in it, like this example:
```
postgresql = {
    "user": "<your-user-name>",
    "password": "********",
    "host": "<your-host>", # example: localhost
    "port": 5432, # postgres default port
    "db": "<your-db-name>"
    }
```

## Telegram bot configurations
Create `teleconfig.py` in the root of project and fill the properties like the example below :
```
API_ID = <your-app-id>
NAME = '<your-bot-name>'
API_HASH = "<your-api-hash>"
BOT_TOKEN = '<your-bot-token>'
CHAT_ID = "<default-chat-id>"

# if you have proxy add your proxy info
PROXY = {
    'scheme': 'socks5',
    'hostname': 'localhost',
    'port': 9999,
}

```

# Run

Run a terminal in the root of project, then if you want to run flask app, run this command:
```
python3 server.py 
```
And if you want to run telegram bot, run this one:
```
python3 telebot.py
```

Then load the web page on your browser on `127.0.0.1:5000`. Set your configurations and press on the search bottom.

