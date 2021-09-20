
from numpy import cumsum as np_cumsum, zeros as np_zeros

from .. cat.tools import Tools
tools = Tools()

class TriArb():
	def __init__(self, vertexes, base_pair=None):
		self.vertexes = vertexes # list of OrderBook objects (classes)
		self.base_pair = base_pair or vertexes[0].get_tickers() # e.g.['btc', 'zar']
		self.path = None
		self._initialise_pass(start_up=True)

	# --- >GET< methods
	def get_vertex(self, position):
		index = position - 1
		return self.vertexes[index]

	def get_base_pair(self):
		return self.base_pair

	def get_path(self):
		return self.path

	# --- >SET< methods
	# Note: Must be run in order [1], [*2], [3], [4]
	# 	*run only at start-up, when class is instantiated
	# [1]
	def _set_vertexes_order(self, base_pair):
		r = [None, None, None]
		for vertex in self.vertexes:
			if sorted(vertex.get_tickers()) == sorted(base_pair):
				r[0] = vertex
			elif base_pair[1] in vertex.get_tickers():
				r[1] = vertex
			else:
				r[2] = vertex
		self.vertexes = r[::]

	# [2]
	def _set_path(self, base_pair):
		r = [base_pair] # [[],]
		for i in (2,3):
			r.append(tools.dominoes(r[-1], self.get_vertex(i).get_tickers())[-1])
		self.path = r[::]

	# [3]
	def _set_vertexes_pairs(self):
		for i in (1,2,3):
			self.get_vertex(i).set_pair(self.path[i-1])

	# [4]
	def _set_vertexes_sides(self):
		for i in (1,2,3):
			# {bridge currency} is always bought at {i} and sold at {i+1}
			# {base currency} determines {side} for buy/sell
			self.get_vertex(i).set_side("bids")
			if self.get_vertex(i).get_tickers()[0] == self.get_vertex(i).get_pair()[1]:
				self.get_vertex(i).set_side("asks")

	# [container] for [1],[2],[3],[4]
	def _initialise_pass(self, base_pair=None, start_up=False):
		base_pair = base_pair or self.base_pair
		self._set_vertexes_order(base_pair=base_pair)
		# ._set_path must only be executed once, when class is instantiated
		if start_up:
			self._set_path(base_pair=base_pair)
		self._set_vertexes_pairs() # ? does this need to be done everytime, or just once as well ---------------
		self._set_vertexes_sides()

	# [core] {{{*}}}
	def _simulate_trade(self, order, offers):
		# get path from currency 1 -> currency 2
		pair1, pair2 = list(order[-1].keys()), list(offers.keys())
		curr = tools.dominoes(pair1, pair2)[-1]

		# simulate a completed trade (or order)

		offers_filled = np_zeros(len(offers[curr[0]]))
		for i, offer in enumerate(np_cumsum(offers[curr[0]])):
			if order[-1][curr[0]] >= offer:
				offers_filled[i] = 1
			else: # order < offer, i.e. partially fulfilled
				offers_filled[i] = (order[-1][curr[0]]-sum(offers[curr[0]][:i])) / (offer-sum(offers[curr[0]][:i]))
				break
		r_order = round(sum(offers_filled * offers[curr[0]]), 8)
		r_offer = round(sum(offers_filled * offers[curr[1]]), 8)
		order.append({curr[0]: r_order})
		order.append({curr[1]: r_offer})
		return order

	# v1.0.001 [start] --->
	# [core] {{{*}}}
	def _simulate_trade_top1(self, order, offers):
		# get path from currency 1 -> currency 2
		pair1, pair2 = list(order[-1].keys()), list(offers.keys())
		curr = tools.dominoes(pair1, pair2)[-1]

		# simulate a completed trade (or order)
		offers_filled = np_zeros(len(offers[curr[0]]))
		for i, offer in enumerate(np_cumsum(offers[curr[0]])):
			if i == 0:
				if order[-1][curr[0]] >= offer:
					offers_filled[i] = 1
				else: # order < offer, i.e. partially fulfilled
					offers_filled[i] = (order[-1][curr[0]]-sum(offers[curr[0]][:i])) / (offer-sum(offers[curr[0]][:i]))
					break
		r_order = round(sum(offers_filled * offers[curr[0]]), 8)
		r_offer = round(sum(offers_filled * offers[curr[1]]), 8)
		order.append({curr[0]: r_order})
		order.append({curr[1]: r_offer})
		return order
	# < --- v2.0.001 [end]

	# [core] {{{}*}}
	def _pass_order(self, order): # base_pair=None

		def is_order_capped(r):
			for i, v in enumerate(r[:-1:]):
				if r[i].keys() == r[i+1].keys():
					values = sorted([
						float(list(r[i].values())[0]),
						float(list(r[i+1].values())[0])])
					# v2.0.001
					# if values[0] == 0:
					# 	return False
					# else:
					if values[1]/values[0] > 1.0001: # 0.01%
						return True
			return False

		# pass order through each vertex
		# self._initialise_pass(base_pair=base_pair)
		r = order[::]
		for i in (2,1):
			# v2.0.001
			r = self._simulate_trade(r, self.get_vertex(i).get_volumes(_side=True))
		# if the order get's capped, we need to pass it back through all vertexes
		if is_order_capped(r):
			for i in (1,2,3):
				# v2.0.001
				r = self._simulate_trade(r, self.get_vertex(i).get_volumes(_side=True))
			# take 2nd pass only
			r = r[-6:][::-1]
		return r[::-1]

	# [core] {{{}}*}
	def get_arb(self): # ---------------- Currently set up to pass only 1 vertex ----------------------------------
		# pass, in turn, all orders of vertex {i}, through all vertexes
		r = []
		for i in (3,): #(1,2,3)
			base_pair = self.get_vertex(i).get_pair()
			orders = self.get_vertex(i).get_volumes(_side=True)
			for j in range(len(orders[base_pair[0]])):
				r.append(self._pass_order(
					[
						{base_pair[1]: orders[base_pair[1]][j]},
						{base_pair[0]: orders[base_pair[0]][j]}
					]))
		return r

	# ad-hoc
	def _format_result(self, r):
		def calc_arbitrage(r):
			return round(100*(r[-1]["zar"]/r[0]["zar"]-1), 2)
		def r_min(r):
			return [v for i,v in enumerate(r) if i in (0,1,3,5)]
		def special_round(r):
			def get_key(d):
				return str(list(d.keys())[0])
			def get_value(d):
				return float(list(d.values())[0])
			return [{get_key(v):round(get_value(v),2)} if get_key(v) in ["zar", "eur", "xrp"] else {get_key(v):get_value(v)} for v in r]

		return {"results": [{"arbitrage": calc_arbitrage(v), "path": special_round(r_min(v))} for v in r]}

if __name__ == '__main__':
	_VERSION = "v1.0.00"
	print("\nversion:", _VERSION)