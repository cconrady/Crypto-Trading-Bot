
class Tools():
	def __init__(self):
		pass

	def dct_down_one(self, dct):
		return list(dct.values())[0]

	def capitalise(self, str):
		return str[0].upper() + str[1::]

	def get_alphanum_id(self):
		from random import choices as random_choices
		CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWQYZ0123456789"
		return "".join(random_choices([C for C in CHARS], k=12))

	def get_client_timestamp(self):
		from datetime import datetime as dt
		return dt.now().strftime("%Y-%m-%dT%H:%M:%S")

	def dominoes(self, pair1, pair2):
		"""
		Like in the game Dominoes, take two unordered 'objects', and ...
			return the ordered pair, with the common side facing.
		e.g. [[x, o],[y, o]] -> [[x, o],[o, y]]
		"""
		def set_to_str(a_set):
			if a_set:
				return str(list(a_set)[0])
			return None
		pair1 = set(pair1)
		pair2 = set(pair2)
		shared = pair1.intersection(pair2)
		start, end  = pair1 - shared, pair2 - shared
		return [[set_to_str(start), set_to_str(shared)], [set_to_str(shared), set_to_str(end)]]

	def remove_list_dups(self, lst):
		r = []
		for item in lst:
			if item not in r:
				r.append(item)
		return r

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("version:", _VERSION)