
# class inheritance
from ..general import General

# local packages
from requests import get as requests_get

class Kraken(General):
	def __init__(self):
		super().__init__()
		# override properties of parent class (General)
		self.url = {
			"order_book": "https://api.kraken.com/0/public/Depth",
			"timestamp_server": "https://api.kraken.com/0/public/Time"
		}
		self._PAIR_LINGO = {"BTC": "XBT", "DOGE": "XDG"}

	# --- >SET< methods (add to parent class)
	def _request_server_timestamp(self):
		from datetime import datetime as dt
		r = requests_get(self.url["timestamp_server"])
		if r.status_code == 200:
			return dt.fromtimestamp(r.json()["result"]["unixtime"]).strftime('%Y-%m-%dT%H:%M:%S') # ISO 8601
		return None

	def _request_order_book(self):
		r = requests_get(self.url["order_book"], params={"pair": self.pair})
		if r.status_code == 200:
			data = r.json()
			order_book = list(data["result"].values())[0]
			order_book["asks"] = [{"price": v[0], "volume": v[1]} for v in order_book["asks"]]
			order_book["bids"] = [{"price": v[0], "volume": v[1]} for v in order_book["bids"]]
			return (r.status_code, order_book)
		return (r.status_code, {})

	def send_request(self):
		self.timestamp["client"] = self._request_client_timestamp()
		self.timestamp["server"] = self._request_server_timestamp()
		self.status_code, self.order_book = self._request_order_book()

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)