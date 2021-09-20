# Crypto Arbitrage Tracker and Trading Bot

The cryptocurrency abitrage tracker and trading bot is built using [Python](https://www.python.org/) (core), [R](https://www.r-project.org/) (vis), and [PostgreSQL](https://www.postgresql.org/) (database). It calculates in real time the abitrage premium of Bitcoin (and other cryptocurrencies) trading between [Kraken](https://www.kraken.com/) (international exchange) and [Luno](https://www.luno.com/)/ [VALR](https://www.valr.com/) (local South African exchange(s)).

<p align="center">
  <img src="assets/splash.JPG"/>
</p>

## Installation

*1.* You'll need to setup a working version of [PostgreSQL](https://www.postgresql.org/). You can find the installation instructions [here](https://www.postgresql.org/). 

*2.* Create a db 

```python

class PostgreSQL():

  def __init__(self, db_name):
    self.db_name = db_name
    self._db_user = "postgres"
    self._db_password = "password"
    self._db_host = "localhost"
    self._db_port = "5432"
    self._connection = None
    
```

You can use any package manager you like (conda, pip, etc.) - you may even choose not to use any! Whichever path you take, make sure to have the following python packages installed, and the correct python version.

```
python==3.9.7
numpy==1.21.2
requests==2.26.0
psycopg2==2.9.1
```

You'll nedd to create 

```python

pg = PostgreSQL("catdb")
    
```