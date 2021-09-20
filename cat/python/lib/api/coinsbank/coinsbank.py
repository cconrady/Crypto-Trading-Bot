
# class inheritance
from ..general import General

# local packages
from requests import get as requests_get

class Coinsbank(General):
	def __init__(self):
		super().__init__()
		# override properties of parent class (General)
		self.url = {
			"order_book": "https://coinsbank.com/api/bitcoincharts/orderbook/",
			"timestamp_server": ""
		}

	# --- >SET< methods (add to parent class)
	def _request_server_timestamp(self):
		"""Coinsbank api doesn't seem to have one."""
		return None

	def _request_order_book(self):
		r = requests_get(self.url["order_book"] + self.pair)
		if r.status_code == 200:
			data = r.json()
			order_book = {}
			order_book["asks"] = [{"price": v[0], "volume": v[1]} for v in data["asks"]]
			order_book["bids"] = [{"price": v[0], "volume": v[1]} for v in data["bids"]]
			return (r.status_code, order_book)
		return (r.status_code, {})

	def send_request(self):
		self.timestamp["client"] = self._request_client_timestamp()
		self.timestamp["server"] = self._request_server_timestamp()
		self.status_code, self.order_book = self._request_order_book()

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)