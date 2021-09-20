
def main():

	from lib.sql.postgresql.postgresql import PostgreSQL
	from lib.cat.tools import Tools

	# ----------------------------------------------------------------------------------------
	# 									PART 1: Arbitrage
	# ----------------------------------------------------------------------------------------

	# ----------------------------------------------------------------------------------------
	# [1.] Fetch data from table "catdb.arb"

	pg = PostgreSQL("catdb") # <---------- INSERT YOUR database NAME HERE (if different from 'init.sql') ----- !!!
	tools = Tools()

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

		-- [3] GET LIST OF LATEST REQUEST_IDS
		DROP TABLE IF EXISTS tmp_request_ids;
		CREATE TEMPORARY TABLE tmp_request_ids AS
		SELECT 
			ra.request_id
		FROM requests AS ra
		RIGHT JOIN tmp_requests_latest AS rb ON ra.api_id = rb.api_id AND ra.client_timestamp = rb.client_timestamp
		LEFT JOIN apis AS ap ON ap.api_id = ra.api_id;

		--* [4] GET RESULTS
		SELECT market, coin, arbitrage
		FROM arbs
		WHERE 
			request_id1 IN (SELECT request_id FROM tmp_request_ids)
		AND request_id2 IN (SELECT request_id FROM tmp_request_ids)
		AND request_id3 IN (SELECT request_id FROM tmp_request_ids);
	"""

	(columns, rows) = pg.fetch_all(query)

	tbl_arbs = pg.sql_tbl_to_py_obj({
		"columns": columns,
		"rows": rows
	}, orient="row")

	# ----------------------------------------------------------------------------------------
	# [2.] Convert 'arbitrage' data into tabular format {tbl} & sql insert format {sql_data}

	tbl = {"coin": [], "market": [], "price": [], "volume": [], "total": [], "margin": []}
	for item in tbl_arbs:
		for order in item["arbitrage"]["results"]:
			tbl["coin"].append(item["coin"])
			tbl["market"].append(item["market"])
			tbl["total"].append(tools.dct_down_one(order["path"][-1]))
			tbl["volume"].append(tools.dct_down_one(order["path"][-2]))
			tbl["price"].append(round(tbl["total"][-1]/tbl["volume"][-1], 2))
			tbl["margin"].append(order["arbitrage"])

	# df_arbs = pd_DataFrame.from_dict(tbl)
	# df_arbs.to_csv('arb.csv', index=False)

	sql_data = []
	for i,v in enumerate(tools.dct_down_one(tbl)):
		sql_data.append(
			(
				tbl["coin"][i],
				tbl["market"][i],
				tbl["price"][i],
				tbl["volume"][i],
				tbl["total"][i],
				tbl["margin"][i]
			)
		)

	# ----------------------------------------------------------------------------------------
	# [3.] Overwrite data in app_orders & app_status

	# app_orders
	query = """
		INSERT INTO app_orders 
			(coin, market, price, volume, total, margin)
		VALUES
			%s;
	"""
	pg.execute_query("""DELETE FROM app_orders;""")
	pg.insert_many(query=query, data=sql_data)

	# ----------------------------------------------------------------------------------------
	# 										PART 2: Status
	# ----------------------------------------------------------------------------------------

	query = """
		-- A

		-- [i] GET ONLINE APIS
		DROP TABLE IF EXISTS tmp_apis_online;
		CREATE TEMPORARY TABLE tmp_apis_online AS
		SELECT api_id
		FROM apis
		WHERE online = 'TRUE';

		-- [ii] GET LATEST REQUEST DATA for online apis [1]
		DROP TABLE IF EXISTS tmp_requests_latest;
		CREATE TEMPORARY TABLE tmp_requests_latest AS
		SELECT api_id, MAX(client_timestamp) AS client_timestamp
		FROM requests
		WHERE status_code = 200 AND
		api_id IN (SELECT api_id FROM tmp_apis_online)
		GROUP BY api_id;

		-- [iii] GET LIST OF LATEST REQUEST_IDS
		DROP TABLE IF EXISTS tmp_request_ids;
		CREATE TEMPORARY TABLE tmp_request_ids AS
		SELECT 
			ra.request_id
		FROM requests AS ra
		RIGHT JOIN tmp_requests_latest AS rb ON ra.api_id = rb.api_id AND ra.client_timestamp = rb.client_timestamp
		LEFT JOIN apis AS ap ON ap.api_id = ra.api_id;

		-- [iv]
		DROP TABLE IF EXISTS arbs_temp1;
		CREATE TEMP TABLE arbs_temp1 AS
		SELECT *
		FROM arbs
		WHERE 
			request_id1 IN (SELECT request_id FROM tmp_request_ids)
		AND request_id2 IN (SELECT request_id FROM tmp_request_ids)
		AND request_id3 IN (SELECT request_id FROM tmp_request_ids);

		-- B
		DROP TABLE IF EXISTS arbs_temp2;
		CREATE TEMP TABLE arbs_temp2 AS
		SELECT request_id1 as request_id
		FROM arbs_temp1
		UNION
		SELECT request_id2 as request_id
		FROM arbs_temp1
		UNION
		SELECT request_id3 as request_id
		FROM arbs_temp1;

		-- C
		DROP TABLE IF EXISTS arbs_temp3;
		CREATE TEMP TABLE arbs_temp3 AS
		SELECT DISTINCT 
			a.request_id,
			r.api_id,
			r.client_timestamp,
			r.server_timestamp,
			r.ping,
			r.status_code
		FROM arbs_temp2 AS a
		LEFT JOIN requests AS r
		ON a.request_id = r.request_id;

		-- D
		DROP TABLE IF EXISTS app_status;
		CREATE TABLE app_status AS
		SELECT 
			ap.name, ap.ticker1, ap.ticker2, ap.online,
			a.request_id, a.client_timestamp, a.server_timestamp, a.ping, a.status_code
		FROM apis AS ap
		LEFT JOIN arbs_temp3 AS a
		ON ap.api_id = a.api_id
		WHERE ap.online = 'TRUE'
		ORDER BY ap.name, ap.ticker1;
	"""

	pg.execute_query(query)

if __name__ == '__main__':
	_VERSION = "v1.0.00"
	main()
	print("\nversion:", _VERSION)