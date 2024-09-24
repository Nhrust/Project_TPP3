import pyodbc
import os

DEBUG = False
TABLE = "_TAB_" # начало названия таблиц в базе

class Param:
	def __init__(self, name, type_name, buffer_length):
		self.name = name
		self.type_name = type_name
		self.buffer_length = buffer_length

	def __repr__(self):
		return f"{self.name} {self.type_name}({self.buffer_length})"

class Table:
	def __init__(self, base, name) -> None:
		self.base = base
		self.name = name
		self.params = [Param(i.column_name, i.type_name, i.buffer_length) for i in base.cursor.columns(table=name)]

class Table_handler:
	def __init__(self, base, table) -> None:
		self.base = base
		self.table = base.tables[table[len(TABLE):]]

	def add(self, *data, params=None) -> None:
		if params == None:
			if len(data) != len(self.table.params):
				print(f"Fail to add values: [*{data}] to table '{self.table.name}'")
				return
			
			for i, item in enumerate(data):
				if self.table.params[i].type_name in ["char", "varchar"] and item.__class__.__name__ == "str":
					if len(item) > self.table.params[i].buffer_length:
						sliced = item[:self.params[i].buffer_length]
						print(f"!!! WARNING: string too long. Column: {self.table.params[i]}\n!!! '{item}'\n!!! '{sliced}'\n")

			self.base.cursor.execute(f"INSERT INTO {self.table.name} VALUES {tuple(data)}")
			if DEBUG: print(f"INSERT INTO {self.table.name} VALUES {tuple(data)}")
		else:
			self.base.cursor.execute(f"INSERT INTO {self.table.name}({', '.join(params)}) VALUES {tuple(data)}")
			if DEBUG: print(f"INSERT INTO {self.table.name}({', '.join(params)}) VALUES {tuple(data)}")

	def write(self, name, data) -> None:
		try:
			i = [i.name for i in self.params].index(name)
		except ValueError:
			print(f"!!! ERROR: Column '{name}' is not defined in table '{self.table.name[len(TABLE):]}'")
			return

		if self.params[i].type_name in ["char", "varchar"]:
			if len(data) > self.params[i][2]:
				sliced = data[:self.params[i].type_name]
				print(f"!!! WARNING: string too long. Column: {self.params[i]}\n!!! '{data}'\n!!! '{sliced}'\n")
		self.base.cursor.execute(f"INSERT INTO {self.table.name}({name}) VALUES ({data})")

	def get(self, column_name, value) -> list:
		value = value if value.__class__.__name__ != "str" else "\'" + value + "\'"
		selector = f"SELECT * FROM {self.table.name} WHERE {column_name} = {value}"
		self.base.cursor.execute(selector)
		return self.base.cursor.fetchall()

	def set(self, column_name, value, new_column_name, new_value) -> None:
		new_value = new_value if new_value.__class__.__name__ != "str" else "\'" + new_value + "\'"
		try:
			self.base.cursor.execute(f"UPDATE {self.table.name} SET {new_column_name} = {new_value} WHERE {column_name} = {value}")
		except Exception as e:
			print("error in SQL request", f"\nUPDATE {self.table.name} SET {new_column_name} = {new_value} WHERE {column_name} = {value}")

	def get_last_id(self) -> int:
		selector = f"SELECT max(id) FROM {self.table.name}"
		self.base.cursor.execute(selector)
		return selector[0]

	def delete(self, column_name, value):
		value = value if value.__class__.__name__ != "str" else "\'" + value + "\'"
		self.base.cursor.execute(f"DELETE FROM {self.table.name} WHERE {column_name} = {value}")

class SQL_base:
	def __init__(self, database, driver="Driver=ODBC Driver 17 for SQL Server") -> None:
		server = os.getenv("SQL_SERVER")
		self.base = pyodbc.connect(f"{driver};Server={server};Database={database};Trusted_Connection=yes;encoding=utf-8")
		self.cursor = self.base.cursor()
		self.tables = dict()
		
		for table in self.get_tables_by_key(TABLE):
			self.tables[table[len(TABLE):]] = Table(self, table)
		
	def get_tables_by_key(self, key) -> str:
		for table in self.cursor.tables():
			if key not in table.table_name:
				continue
			yield table.table_name

	def show(self) -> None:
		for table in self.cursor.tables():
			table_name = str(table.table_name)
			
			if TABLE not in table_name:
				continue

			print(table_name[len(TABLE):])
			for row in self.cursor.columns(table=table_name):
				print(f"  {row.column_name} > {row.type_name}({row.buffer_length})")
			print()

	def create_table(self, name, *columns) -> None:
		self.cursor.execute(f"CREATE TABLE {TABLE}{name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")
		self.tables[name] = Table(self, TABLE + name)

	def drop_table(self, name) -> None:
		self.cursor.execute(f"DROP TABLE {TABLE}{name}")
		del self.tables[name]

	def CREATE(self, name, *columns) -> None:
		self.cursor.execute(f"CREATE TABLE {name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")

	def DROP(self, name) -> None:
		self.cursor.execute(f"DROP TABLE {name}")
	
	def GET(self, table, column_name, value) -> list:
		selector = f"SELECT * FROM {table} WHERE {column_name} = {value}"
		self.cursor.execute(selector)
		return self.cursor.fetchall()

	def __getitem__(self, name) -> Table_handler:
		return Table_handler(self, TABLE + name)

	def commit(self) -> None:
		self.base.commit()