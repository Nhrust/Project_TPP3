import pyodbc
import os

DEBUG = True
TABLE = "_TAB_"
CHAT = "_CHT_"
GROUP_CHAT = "_GCH_"
GROUP_CHAT_USERS = "_GCU_"

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
			if self.base.DEBUG: print(f"INSERT INTO {self.table.name} VALUES {tuple(data)}")
		else:
			self.base.cursor.execute(f"INSERT INTO {self.table.name}({', '.join(params)}) VALUES {tuple(data)}")
			if self.base.DEBUG: print(f"INSERT INTO {self.table.name}({', '.join(params)}) VALUES {tuple(data)}")

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

	def get(self, column_name, value, select_column="*", select_type="=") -> list:
		"""SELECT {select_column} FROM ... WHERE {column_name} {select_type} {value}"""
		value = value if value.__class__.__name__ != "str" else "\'" + value + "\'"
		selector = f"SELECT {select_column} FROM {self.table.name} WHERE {column_name} {select_type} {value}"
		if self.base.DEBUG: print(selector)
		self.base.cursor.execute(selector)
		return self.base.cursor.fetchall()
	
	def GET(self, where, select_column="*") -> list:
		"""SELECT {select_column} FROM ... WHERE {where}"""
		selector = f"SELECT {select_column} FROM {self.table.name} WHERE {where}"
		if self.base.DEBUG: print(selector)
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
		return self.base.cursor.fetchall()[0][0]

	def delete(self, column_name, value):
		value = value if value.__class__.__name__ != "str" else "\'" + value + "\'"
		self.base.cursor.execute(f"DELETE FROM {self.table.name} WHERE {column_name} = {value}")

class SQL_base:
	DEBUG = True

	def __init__(self, database, driver="ODBC Driver 17 for SQL Server") -> None:
		server = os.getenv("SQL_SERVER")
		self.datsbase = database
		self.base: pyodbc.Connection = pyodbc.connect(f"Driver={driver};Server={server};Database={database};Trusted_Connection=yes;encoding=utf-8")
		self.cursor: pyodbc.Cursor = self.base.cursor()
		self.tables = dict()
		
		for table in self.get_tables_by_key(TABLE):
			self.tables[table[len(TABLE):]] = Table(self, table)
		
		if self.DEBUG: print("# SQL_base.__init__()\n\tfind tables:", *list(self.tables.keys()))
		
	def get_tables_by_key(self, key: str=None) -> str:
		if key == None:
			self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
			return [table[2] for table in self.cursor.fetchall()]
		self.cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME LIKE '{key}%'")
		return [table[2] for table in self.cursor.fetchall() if key in table[2]]

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
		if self.DEBUG: print(f"# SQL_base.create_table(self, {columns})\n\tCREATE TABLE {TABLE}{name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")
		self.cursor.execute(f"CREATE TABLE {TABLE}{name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")
		self.commit()
		self.tables[name] = Table(self, TABLE + name)

	def drop_table(self, name) -> None:
		if self.DEBUG: print(f"# SQL_base.drop_table(self, {name})\n\tDROP TABLE {TABLE}{name}")
		try:
			self.cursor.execute(f"DROP TABLE {TABLE}{name}")
			self.commit()
		except Exception as e:
			print(e)
		try:
			del self.tables[name]
		except Exception as e:
			print(e)
	
	def ADD(self, name, data, params=None):
		"""INSERT INTO {name} ( {params} ) VALUES {data}"""
		if params == None:
			self.cursor.execute(f"INSERT INTO {name} VALUES {tuple(data)}")
			if self.DEBUG: print(f"INSERT INTO {name} VALUES {tuple(data)}")
		else:
			self.cursor.execute(f"INSERT INTO {name}({', '.join(params)}) VALUES {tuple(data)}")
			if self.DEBUG: print(f"INSERT INTO {name}({', '.join(params)}) VALUES {tuple(data)}")

	def CREATE(self, name, *columns) -> None:
		if self.DEBUG: print(f"# SQL_base.CREATE(self, {name}, {columns})\n\tCREATE TABLE {name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")
		self.cursor.execute(f"CREATE TABLE {name}({columns[0]}{''.join([', ' + i for i in columns[1:]])})")
		self.commit()

	def DROP(self, name) -> None:
		"""DROP TABLE {name}"""
		if self.DEBUG: print(f"# SQL_base.DROP(self, {name})\n\tDROP TABLE {name}")
		self.cursor.execute(f"DROP TABLE {name}")
		self.commit()
	
	def GET(self, table, where, select_column="*") -> list:
		"""SELECT {select_column} FROM {table} WHERE {where}"""
		selector = f"SELECT {select_column} FROM {table} WHERE {where}"
		if self.DEBUG: print(f"# SQL_base.GET(self, {table}, {where}, {select_column})\n\t{selector}")
		self.cursor.execute(selector)
		finded = self.cursor.fetchall()
		if self.DEBUG: print("finded:", finded)
		return finded

	def table(self, name) -> Table_handler:
		return Table_handler(self, TABLE + name)

	def commit(self) -> None:
		if self.DEBUG: print("# SQL_base.commit()")
		self.base.commit()
	
	def RESET(self):
		self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
		for table in self.cursor.fetchall():
			self.cursor.execute(f"DROP TABLE {table[2]}")
		self.base.commit()
		self.tables = dict()