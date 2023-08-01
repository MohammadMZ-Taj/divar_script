# Divar Script
A simple python script which collects house information (in [Shiraz](https://en.wikipedia.org/wiki/Shiraz)) from divar.ir and sends to telegram.

# Technologies and Frameworks
sqlalchemy, BeautifulSoap4, postgresql, flask and telegram apis

# Requirements
The Project requires these packages:
```
beautifulsoup4==4.12.2
Flask==2.3.2
psycopg2-binary==2.9.6
PySocks==1.7.1
requests==2.31.0
SQLAlchemy==2.0.19
SQLAlchemy-Utils==0.41.1
...
```
and some others.

Install all python packages from requirements.txt:
```
pip install -r requirements.txt
```
### Database configurations
You also need to have [Postgresql](https://www.postgresql.org/) on your system. Create local_settings.py and add your database configuration in it, like this example:
```
postgresql = {
    "user": "your-user-name",
    "password": "********",
    "host": "your-host", # example: localhost
    "port": 5432, # postgres default port
    "db": "your-db-name"
    }
```
# How to run
Set your `bale bot api` you got from @botfather in `config.py`.

You can get the chat id you want the bot to send message to when you go to `web.bale.ai`.

For example this chat is the main one `https://web.bale.ai/chat/6425583673` and the id is `6425583673`. Add "a" between each chat id.

Run a terminal in root of project and run the server:
```
python3 server.py 
```
Then load the web page on your browser. Set your own configurations and press on the search bottom.

### Proxies
You can set proxies in `config.py`.
