
from numpy import array as np_array

class OrderBook():
	def __init__(self, api, ticker1, ticker2, order_book, request_id=None):
		# ... on init
		self.api = api # kraken, luno etc.
		self.ticker1 = ticker1 # 1 ticker1 ~ x ticker2
		self.ticker2 = ticker2 # 1 ticker1 ~ x ticker2
		self.order_book = order_book
		self.request_id = request_id or []
		# ... outside of init
		self.prices = None; self._set_prices()
		self.volumes = None; self._set_volumes()	
		self._pair = None # for use in TriArb()
		self._side = None # for use in TriArb()

	# --- >GET< methods
	def get_api(self):
		return self.api

	def get_tickers(self):
		return [self.ticker1, self.ticker2]

	def get_order_book(self):
		return self.order_book

	def get_request_id(self):
		return self.request_id

	def get_prices(self, _side=False):
		if _side:
			return self.prices[self._side]
		return self.prices

	def get_volumes(self, _side=False):
		if _side:
			return self.volumes[self._side]
		return self.volumes

	def get_pair(self):
		return self._pair

	def get_side(self):
		return self._side

	# --- >SET< methods
	def set_pair(self, pair):
		self._pair = pair

	def set_side(self, side):
		self._side = side

	def _set_prices(self):
	# "'parsing' from order book, and reformatting"
		asks = {self.ticker1: np_array([1 for order in self.order_book["asks"]]),
				self.ticker2: np_array([float(order["price"]) for order in self.order_book["asks"]])}
		bids = {self.ticker1: np_array([1 for order in self.order_book["bids"]]),
				self.ticker2: np_array([float(order["price"]) for order in self.order_book["bids"]])}
		self.prices = {"asks": asks, "bids": bids}

	def _set_volumes(self):
	# "'parsing' from order book, and reformatting"
		asks = {self.ticker1: np_array([float(order["volume"]) for order in self.order_book["asks"]]) * self.prices["asks"][self.ticker1],
				self.ticker2: np_array([float(order["volume"]) for order in self.order_book["asks"]]) * self.prices["asks"][self.ticker2]}
		bids = {self.ticker1: np_array([float(order["volume"]) for order in self.order_book["bids"]]) * self.prices["bids"][self.ticker1],
				self.ticker2: np_array([float(order["volume"]) for order in self.order_book["bids"]]) * self.prices["bids"][self.ticker2]}
		self.volumes = {"asks": asks, "bids": bids}

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("\nversion:", _VERSION)