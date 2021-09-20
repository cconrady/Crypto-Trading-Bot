# cat libraries
## api libraries
from lib.api.alpha.alpha import Alpha
from lib.api.kraken.kraken import Kraken
from lib.api.coinsbank.coinsbank import Coinsbank
from lib.api.luno.luno import Luno
from lib.api.valr.valr import Valr


## sql & general
from lib.sql.postgresql.postgresql import PostgreSQL
from lib.cat.tools import Tools

# external libraries
from json import dumps as json_dump

## parallel computing
from multiprocessing import Pool
from os import getpid

# ----------------------------------------------------------------------------------------
# [1.] Fetch data from table "catdb.apis"

pg = PostgreSQL("catdb") # <---------- INSERT YOUR database NAME HERE (if different from 'init.sql') ----- !!!

(columns, rows) = pg.fetch_all("""SELECT * FROM apis WHERE online = 'TRUE';""")

tbl_apis = pg.sql_tbl_to_py_obj({
	"columns": columns,
	"rows": rows
}, orient="column")

# ----------------------------------------------------------------------------------------
# [2.] Make api requests, save to "xxx_catdb.requests" sql db

query = """
	INSERT INTO requests 
		(request_id, api_id, client_timestamp, server_timestamp, ping, status_code, order_book)
	VALUES
		(%s, %s, %s, %s, %s, %s, %s);
"""

# instantiate apis (in batch)
apis = []
tools = Tools()
for i, name in enumerate(tbl_apis["name"]):
	if name[tbl_apis["online"][i]]: # if api is online
		pair = "_".join([tbl_apis["ticker1"][i], tbl_apis["ticker2"][i]])
		short_name = "_".join([name[:3], tbl_apis["ticker1"][i][:3], tbl_apis["ticker2"][i][:3]]) # limit ticker to 3 char each in name id
		# instantiate 
		apis.append(locals()[tools.capitalise(name)]())
		apis[-1].set_pair(pair=pair)
		apis[-1].set_name(name=short_name)

# apis.pop()

# make api requests (in parallel)
def execute_request(api):
	from timeit import default_timer
	# send get request to api
	start_time = default_timer()
	api.send_request()
	end_time = default_timer()
	ping = int(1000*(end_time - start_time)) # in ms

	# save api request data
	pg.insert_one(query, [1,1],
		tools.get_alphanum_id(),
		api.get_name(),
		api.get_timestamp(key="client"),
		api.get_timestamp(key="server"),
		ping,
		api.get_status_code(),
		json_dump(api.get_order_book())
	)

	return [{"process_id": api.get_name(), "status": api.get_status_code(), "ping": ping}]

if __name__ == '__main__': # isolate above code from Pool() method calls
	with Pool() as pool:
		result = pool.map(execute_request, apis)
	for item in result:
		print(item)