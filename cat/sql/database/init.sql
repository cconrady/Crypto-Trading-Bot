--------------------------------------------------------------------------------------------
--	 								SECTION 1 - CREATE TABLES
--------------------------------------------------------------------------------------------

CREATE DATABASE catdb WITH ENCODING 'UTF8' LC_COLLATE='English_United Kingdom' LC_CTYPE='English_United Kingdom';

DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS apis;
DROP TABLE IF EXISTS arbs;

--- [1] apis
CREATE TABLE apis (
	api_id CHAR(11) NOT NULL -- kraken (kra) + btc/eur (btceur)
	,name VARCHAR(20) NOT NULL -- kraken, luno, valr, alpha
	,ticker1 VARCHAR(5) NOT NULL -- btc, ltc, eth, eur, zar...
	,ticker2 VARCHAR(5) NOT NULL -- btc, ltc, eth, eur, zar...
	,online BOOL NOT NULL DEFAULT FALSE --
	,PRIMARY KEY(api_id)
);

--- [2] requests
CREATE TABLE requests (
	request_id CHAR(12) NOT NULL -- 12 character of [a-zA-Z0-9]
	,api_id CHAR(11) NOT NULL -- kraken (kra) + btc/eur (btceur) 
	,client_timestamp TIMESTAMPTZ NOT NULL -- client datetime
	,server_timestamp TIMESTAMPTZ -- server datetime
	,ping INT -- ping in ms
	,status_code INT NOT NULL -- 200, 400 etc
	,order_book JSON NOT NULL -- JSON order book data {"price": etc, "volume": etc}
	,PRIMARY KEY(request_id)
	,CONSTRAINT fk_apis
    	FOREIGN KEY(api_id) 
			REFERENCES apis(api_id)
);

--- [3] arbs
CREATE TABLE arbs (
	arb_id CHAR(12) NOT NULL -- 12 character of [a-zA-Z0-9]
	,client_timestamp TIMESTAMPTZ NOT NULL -- client (this computer) datetime
	,request_id1 CHAR(12) NOT NULL -- 12 character of [a-zA-Z0-9]
	,request_id2 CHAR(12) NOT NULL -- 12 character of [a-zA-Z0-9]
	,request_id3 CHAR(12) NOT NULL -- 12 character of [a-zA-Z0-9]
	,market VARCHAR(20) NOT NULL-- eg. kraken, luno, valr, alpha
	,coin VARCHAR(4) NOT NULL -- eg. BTC, ETH, LTC, XRP, etc.
	,arbitrage JSON NOT NULL -- JSON arb data
	,PRIMARY KEY(arb_id)
);

--- [4.1] app_orders
DROP TABLE IF EXISTS app_orders;
CREATE TABLE app_orders (
-- 	id serial PRIMARY KEY -- autoincerement primary key (index)
	coin VARCHAR(4) NOT NULL -- eg. BTC, ETH, LTC, XRP, etc.
	,market CHAR(3) NOT NULL -- eg. kra, lun, val, ice
	,price FLOAT NOT NULL -- eg. Rxxx.xx (always quoted in Rands)
	,volume FLOAT NOT NULL -- eg. quoted in native 'coin'
	,total FLOAT NOT NULL-- eg. Rxxx.xx (always quoted in Rands)
	,margin FLOAT NOT NULL -- eg. 5%
);

--- [4.2] app_status
DROP TABLE IF EXISTS app_status;
-- CREATED BY 'fetch.py'

-- *These tables are created in Python, and overwritten each time.
-- *R webapp will fetch and populate this data.
-- *This is to avoid manipulating JSON data in R.

--------------------------------------------------------------------------------------------
-- 								SECTION 2 - POPULATE TABLES
--------------------------------------------------------------------------------------------

--- [1] apis
INSERT INTO apis 
	(api_id, name, ticker1, ticker2)
VALUES
	('alp_eur_zar', 'alpha', 'eur', 'zar')
	,('kra_btc_eur', 'kraken', 'btc', 'eur')
	,('kra_eth_eur', 'kraken', 'eth', 'eur')
	,('lun_btc_zar', 'luno', 'btc', 'zar')
	,('lun_eth_zar', 'luno', 'eth', 'zar')
	;

-- *The rest of the tables are programmatically populated.

--------------------------------------------------------------------------------------------
-- 								SECTION 3 - INITIALISE
--------------------------------------------------------------------------------------------

UPDATE apis SET online = 'TRUE';