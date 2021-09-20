
class General():
	def __init__(self):
		# set by user
		self.name = None # kraken, luno, valr, etc.
		self.pair = None # "xbt_eur" -> "xbteur" (case-insensitive)
		# set in class (override)
		self._PAIR_LINGO = dict() # "XBT" is "BTC", api specific lingo
		self.url = dict() # "order book" & "server time" api urls
		# created on 'send_request'
		self.order_book = dict() # "asks" & "bids"
		self.timestamp = dict() # "server" & "client"
		self.status_code = None
		
	# --- >GET< methods
	def get_name(self):
		return self.name

	def get_pair(self):
		return self.pair

	def get_pair_lingo(self):
		return self._PAIR_LINGO

	def get_url(self, key=None):
		if key and type(self.url) == dict:
			return self.url[key]
		return self.url

	def get_timestamp(self, key=None):
		if key and type(self.timestamp) == dict:
			return self.timestamp[key]
		return self.timestamp

	def get_status_code(self):
		return self.status_code

	def get_order_book(self):
		return self.order_book

	def get_bids(self):
		if "bids" in self.order_book.keys():
			return self.order_book["bids"]
		return list()

	def get_asks(self):
		if "asks" in self.order_book.keys():
			return self.order_book["asks"]
		return list()

	# --- >SET< methods
	def set_name(self, name):
		self.name = name.lower()

	def set_pair(self, pair):
		pair = pair.upper()
		if self._PAIR_LINGO:
			self.pair = "".join([self._PAIR_LINGO[p] if p in self._PAIR_LINGO.keys() else p for p in pair.split("_")])
		else:
			self.pair = "".join(pair.split("_"))

	def _request_client_timestamp(self):
		from datetime import datetime as dt
		return dt.now().strftime("%Y-%m-%dT%H:%M:%S") # ISO 8601

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)