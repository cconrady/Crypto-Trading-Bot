
# class inheritance
from ..general import General

class Luno(General):
	def __init__(self):
		super().__init__()
		# override url property of parent class
		self.url = {
			"order_book": "https://api.luno.com/api/1/orderbook_top"
		}
		self._PAIR_LINGO = {"BTC": "XBT"}

	# --- >SET< methods (add to parent class)
	def _request_order_book(self):
		from datetime import datetime as dt
		from requests import get as requests_get		
		r = requests_get(self.url["order_book"], params={"pair": self.pair})
		if r.status_code == 200:
			data = r.json()
			timestamp_server = data.pop("timestamp")
			timestamp_server = dt.fromtimestamp(round(timestamp_server/1000)).strftime('%Y-%m-%dT%H:%M:%S') # ISO 8601
			return (r.status_code, timestamp_server, data)
		return (r.status_code, None, {})

	def send_request(self):
		self.timestamp["client"] = self._request_client_timestamp()
		self.status_code, self.timestamp["server"], self.order_book = self._request_order_book()

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)