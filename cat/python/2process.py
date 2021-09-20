
def main():

	# arbitrage ('arb') library modules
	from lib.sql.postgresql.postgresql import PostgreSQL
	from lib.cat.orderbook import OrderBook
	from lib.cat.triarb import TriArb
	from lib.cat.tools import Tools

	# local modules needed
	from json import dumps as json_dump
	from collections import Counter

	# ------------------------------------------------------------------------ #
	#                                 PART 1                                   #
	# ------------------------------------------------------------------------ #

	# ----------------------------------------------------------------------------------------
	# [1.] Fetch data from table "xxx_catdb.requests & xxx_catdb.apis"

	pg = PostgreSQL("catdb") # <---------- INSERT YOUR database NAME HERE (if different from 'init.sql') ----- !!!
	tools = Tools()

	# v1.0.00
	query = """
		-- [1] GET ONLINE APIS
		DROP TABLE IF EXISTS tmp_apis_online;
		CREATE TEMPORARY TABLE tmp_apis_online AS
		SELECT api_id
		FROM apis
		WHERE online = 'TRUE';

		-- [2] GET LATEST REQUEST DATA for online apis [1]
		DROP TABLE IF EXISTS tmp_requests_latest;
		CREATE TEMPORARY TABLE tmp_requests_latest AS
		SELECT api_id, MAX(client_timestamp) AS client_timestamp
		FROM requests
		WHERE status_code = 200 AND
		api_id IN (SELECT api_id FROM tmp_apis_online)
		GROUP BY api_id;

		-- [3] FORMAT RESULTS
		SELECT 
			ap.api_id, ap.name, ap.ticker1, ap.ticker2,
			ra.request_id, ra.client_timestamp, ra.order_book
		FROM requests AS ra
		RIGHT JOIN tmp_requests_latest AS rb ON ra.api_id = rb.api_id AND ra.client_timestamp = rb.client_timestamp
		LEFT JOIN apis AS ap ON ap.api_id = ra.api_id
		ORDER BY api_id;
	"""


	(columns, rows) = pg.fetch_all(query)

	tbl_requests = pg.sql_tbl_to_py_obj({
		"columns": columns,
		"rows": rows
	}, orient="row")

	# ----------------------------------------------------------------------------------------
	# [2.] Simulate arbitrage across any valid triangle arbitrage opportunity
	# 	[a.1] Find all valid triangle arbitrages

	tbl_min = [[row["api_id"], row["ticker1"], row["ticker2"]] for row in tbl_requests]

	triangles = []
	all_combinations = ([i[1::],j[1::],k[1::]] for i in tbl_min for j in tbl_min for k in tbl_min)
	for combination in all_combinations:
		unpacked = [item for sublist in combination for item in sublist]
		counts = dict(Counter(unpacked))
		test = [v == 2 for k, v in counts.items()] # a valid triangle has 2x 3 distinct currencies
		if all(test):
			triangles.append(combination)

	# ----------------------------------------------------------------------------------------
	# 	[a.2] Order vertex (side of triangle) pairs to form valid paths
	for i,item in enumerate(triangles):
	    triangles[i] = [tools.dominoes(item[i], item[(i+1) % 3])[0] for i,v in enumerate(item)]

	# remove duplicates
	triangles = tools.remove_list_dups(triangles)

	# ----------------------------------------------------------------------------------------
	# 	[a.3] Filter on ZAR, EUR base pair

	base_pair = ["zar", "eur"]
	triangles = [path for path in triangles if path[0] == base_pair]

	# [
	# 	[['zar', 'eur'], ['eur', 'btc'], ['btc', 'zar']],
	# 	[['zar', 'eur'], ['eur', 'eth'], ['eth', 'zar']],
	# 	[['zar', 'eur'], ['eur', 'ltc'], ['ltc', 'zar']],
	# 	[['zar', 'eur'], ['eur', 'xrp'], ['xrp', 'zar']]
	# ]

	# ----------------------------------------------------------------------------------------
	# 	[a.4] Re-attach api_id (link to order_book data)

	apis = []
	for path in triangles:
		r1 = []
		for pair in path:
			r2 = []
			for ticker in tbl_min:
				if sorted(pair) == sorted(ticker[1::]):
					r2.append(ticker[0])
			r1.append(r2)
		apis.append(r1)

	# [
	# 	[['sha_eur_zar'], ['kra_btc_eur'], ['lun_btc_zar', 'val_btc_zar', 'ice_btc_zar', 'alt_btc_zar']],
	# 	[['sha_eur_zar'], ['kra_eth_eur'], ['lun_eth_zar']],
	# 	[['sha_eur_zar'], ['kra_ltc_eur'], ['lun_ltc_zar']],
	# 	[['sha_eur_zar'], ['kra_xrp_eur'], ['lun_xrp_zar']]
	# ]

	# ---------------------------------------------------------------------------------------------------TD
	# could load this all (up to here) into a class instance, put in the pairs and exchange
	# names, it returns them order on a base pair?

	# ------------------------------------------------------------------------ #
	#                                 PART 2                                   #
	# ------------------------------------------------------------------------ #

	# THIS IS THE BIG BOY HERE ----------------------------------------------------------------------
	# setup to overwrite, since holding 100's of TriArb classes at once might use a lot of memory,
	# but this can be changed ?
	# -----------------------------------------------------------------------------------------------

	# reformat {tbl_requests} as dict, key = api_id
	r = {}
	for row in tbl_requests:
		r.update({row["api_id"]: row})

	query = """
		INSERT INTO arbs 
			(arb_id, client_timestamp, request_id1, request_id2, request_id3, market, coin, arbitrage)
		VALUES
			(%s, %s, %s, %s, %s, %s, %s, %s);
	"""
	pg.create_connection()
	# getting the arb, & writing result to SQL 'arbs' table
	for row in apis:
		for c1 in row[0]:
			for c2 in row[1]:
				for c3 in row[2]:
					# get arb
					arb = TriArb(
						[
							OrderBook(
								api=r[c1]["api_id"],
								ticker1=r[c1]["ticker1"],
								ticker2=r[c1]["ticker2"],
								order_book=r[c1]["order_book"],
								request_id=r[c1]["request_id"]
							),
							OrderBook(
								api=r[c2]["api_id"],
								ticker1=r[c2]["ticker1"],
								ticker2=r[c2]["ticker2"],
								order_book=r[c2]["order_book"],
								request_id=r[c2]["request_id"]
							),
							OrderBook(
								api=r[c3]["api_id"],
								ticker1=r[c3]["ticker1"],
								ticker2=r[c3]["ticker2"],
								order_book=r[c3]["order_book"],
								request_id=r[c3]["request_id"]
							)
						],
						base_pair=base_pair)
					# prepare data to write to sql 
					data = {
						"arb_id": tools.get_alphanum_id(),
						"client_timestamp": tools.get_client_timestamp(),
						"request_id1": arb.get_vertex(1).get_request_id(),
						"request_id2": arb.get_vertex(2).get_request_id(),
						"request_id3": arb.get_vertex(3).get_request_id(),
						"market": c3.split("_")[0],
						"coin": c3.split("_")[1],
						"arbitrage": arb._format_result(arb.get_arb())
					}
					# write to sql
					pg.insert_one(query, [0,0],
						data["arb_id"],
						data["client_timestamp"],
						data["request_id1"],
						data["request_id2"],
						data["request_id3"],
						data["market"],
						data["coin"],
						json_dump(data["arbitrage"])
					)

	pg.close_connection()

if __name__ == '__main__':
	_VERSION = "v1.0.00"
	main()
	print("\nversion:", _VERSION)

"""

# ----------------------------------------------------------------------------------------
# 										NOTES
# ----------------------------------------------------------------------------------------

# Only process the data from apis that are set to online.