
# class inheritance
from ..general import General

# local packages
from datetime import datetime as dt
from requests import get as requests_get

class Valr(General):
	def __init__(self):
		super().__init__()
		# override url property of parent class
		self.url = {
			"order_book": "https://api.valr.com/v1/marketdata/:currencyPair/orderbook",
			"timestamp_server": "https://api.valr.com/v1/public/time"
		}
		self._PAIR_LINGO = None
		self._API_KEY = "#" # <--------- INSERT YOUR KEY HERE
		self._API_KEY_SECRET = "#" # <--------- INSERT YOUR KEY HERE

	# --- >SET< methods (add to parent class)
	def _request_server_timestamp(self):
		r = requests_get(self.url["timestamp_server"])
		if r.status_code == 200:
			return dt.fromtimestamp(r.json()["epochTime"]).strftime('%Y-%m-%dT%H:%M:%S') # ISO 8601
		return None

	def _sign_request(self, api_key_secret, timestamp, verb, path, body = ""):
		"""See: https://docs.valr.com/"""
		import hashlib
		import hmac
		payload = "{}{}{}{}".format(timestamp,verb.upper(),path,body)
		message = bytearray(payload,'utf-8')
		signature = hmac.new( bytearray(api_key_secret,'utf-8'), message, digestmod=hashlib.sha512).hexdigest()
		return signature

	def _request_order_book(self):
		from time import time as time
		args = {
			"url": self.url["order_book"].replace(":currencyPair", self.get_pair()),
			"api_key_secret": self._API_KEY_SECRET,
			"timestamp": int(time()*1000),
			"verb": "GET",
			"path": None,
			"body": ""
		}
		args["path"] = args["url"].split(".com")[1]

		headers = {
			"X-VALR-API-KEY": self._API_KEY,
			"X-VALR-SIGNATURE": self._sign_request(
				args["api_key_secret"],
				args["timestamp"],
				args["verb"],
				args["path"],
				args["body"]
				),
			"X-VALR-TIMESTAMP": str(args["timestamp"])
		}
		data = {}
		r = requests_get(args["url"], headers=headers, data=data)
		if r.status_code == 200:
			data = r.json()
			order_book = {}
			order_book["asks"] = [{"price": v["price"], "volume": v["quantity"]} for v in data["Asks"]]
			order_book["bids"] = [{"price": v["price"], "volume": v["quantity"]} for v in data["Bids"]]
			return (r.status_code, order_book)
		return (r.status_code, {})

	def send_request(self):
		self.timestamp["client"] = self._request_client_timestamp()
		self.timestamp["server"] = self._request_server_timestamp()
		self.status_code, self.order_book = self._request_order_book()

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)