
from psycopg2 import connect as pg_connect, OperationalError
from psycopg2.extras import execute_values

class PostgreSQL():

	def __init__(self, db_name):
		self.db_name = db_name
		self._db_user = "postgres" # <-------------- INSERT YOUR *SECURE DETAILS HERE
		self._db_password = "password" # <-------------- INSERT YOUR *SECURE DETAILS HERE
		self._db_host = "localhost" # <-------------- INSERT YOUR *SECURE DETAILS HERE
		self._db_port = "5432" # <-------------- INSERT YOUR *SECURE DETAILS HERE
		self._connection = None

	def create_connection(self):
		try:
			self._connection = pg_connect(
				database=self.db_name,
				user=self._db_user,
				password=self._db_password,
				host=self._db_host,
				port=self._db_port,
			)
			self._connection.set_session(autocommit=True)
			if __name__ == "__main__":
				print("Connection to PostgreSQL successful...")
		except OperationalError as e:
			print(f"The error '{e}' occurred.")

	def close_connection(self):
		if self._connection:
			self._connection.close()

	def execute_query(self, query):
		self.create_connection()
		try:
			cursor = self._connection.cursor()
			cursor.execute(query)
			cursor.close()
		except OperationalError as e:
			print(f"The error '{e}' occurred.")
		self.close_connection()

	def fetch_all(self, query):
		self.create_connection()
		try:
			cursor = self._connection.cursor()
			cursor.execute(query)
			result = cursor.fetchall()
			column_names = cursor.description
			cursor.close()
		except OperationalError as e:
			print(f"The error '{e}' occurred.")
		self.close_connection()
		return None or (column_names, result)

	def insert_one(self, query, connection=[1,1], *args):
		if connection[0] == 1:
			self.create_connection()
		try:
			cursor = self._connection.cursor()
			cursor.execute(query, args)
			cursor.close()
		except OperationalError as e:
			print(f"The error '{e}' occurred.")
		if connection[1] == 1:
			self.close_connection()

	def insert_many(self, query, data):
		"""
		e.g.
		query = "INSERT INTO test (a, b) VALUES %s"
		data = [(1,'x'), (2,'y')]
		"""
		self.create_connection()
		try:
			cursor = self._connection.cursor()
			execute_values(cursor, query, data) # template=None, page_size=100
			cursor.close()
		except OperationalError as e:
			print(f"The error '{e}' occurred.")
		self.close_connection()

	# format sql results
	def sql_tbl_to_py_obj(self, tbl, orient="row"):
		def _row_frmt(tbl):
			result = []
			for row in tbl["rows"]:
				result.append({tbl["columns"][i][0]: row[i] for i in range(len(row))})
			return result

		def _col_frmt(tbl):
			result = {}
			for ci, cv in enumerate(tbl["columns"]):
				result[cv[0]] = []
				for ri, rv in enumerate(tbl["rows"]):
					result[cv[0]].append(rv[ci])
			return result

		if orient == "row":
			return _row_frmt(tbl)
		elif orient == "column":
			return _col_frmt(tbl)
		else:
			raise Exception("Param 'orient' must be 'row' or 'column'.")

if __name__ == '__main__':
	_VERSION = "v1.0.000"
	print("\nversion:", _VERSION)