# Crypto Arbitrage Tracker and Trading Bot

This cryptocurrency abitrage tracker and trading bot is built using [Python](https://www.python.org/) (core), [R](https://www.r-project.org/) (vis), and [PostgreSQL](https://www.postgresql.org/) (database). It calculates in real time the abitrage premium of Bitcoin (and other cryptocurrencies) trading between [Kraken](https://www.kraken.com/) (international exchange) and [Luno](https://www.luno.com/)/ [VALR](https://www.valr.com/) (local South African exchange(s)).

<p align="center">
  <img src="assets/splash.JPG"/>
</p>

## Installation

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