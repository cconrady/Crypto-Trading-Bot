
# class inheritance
from ..general import General

class Alpha(General):
	def __init__(self):
		super().__init__()
		# override url property of parent class
		self.url = {
			"order_book": "https://www.alphavantage.co/query"
		}
		self.payload = {
			"function": "CURRENCY_EXCHANGE_RATE",
			"from_currency": "EUR",
			"to_currency": "ZAR",
			"apikey": "XAWN1OVRSV1288BS" # <---- INSERT YOUR API KEY HERE <---------------------------------------------------
		}
		self._PAIR_TERM = None

	def _request_order_book(self):
		from requests import get as requests_get
		r = requests_get(self.url["order_book"], params=self.payload)
		if r.status_code == 200:
			data = r.json()
			order_book = {
				"asks": [
				{
					"price": float(data["Realtime Currency Exchange Rate"]["8. Bid Price"]),
					"volume": 100000000
				}],
				"bids": [
				{
					"price": float(data["Realtime Currency Exchange Rate"]["9. Ask Price"]),
					"volume": 100000000
				}]
			}
			last_updated = data["Realtime Currency Exchange Rate"]["6. Last Refreshed"]
			return (r.status_code, last_updated, order_book)
		return (r.status_code, None, {})

	def send_request(self):
		self.timestamp["client"] = self._request_client_timestamp()
		self.status_code, self.timestamp["server"], self.order_book = self._request_order_book()

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)