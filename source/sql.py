from typing import Any, Callable, Iterable

from cryptography.fernet import Fernet
import threading
import colorama
import pyodbc
import copy
import os

DEBUG = True

TABLE = "_TAB_"
CHAT  = "_CHT_"
BAND  = "_BND_"
GROUP = "_GRP_"

KEY = Fernet(b'ja3SUk5zbKBMHy9IZZpogAysEX0O5g1UFLA_hgDmnnU=')
def encode(string): return str(string).encode().hex()
def decode(string): return bytearray.fromhex(str(string)).decode()
def encrypt(string): return KEY.encrypt(str(string).encode()).decode()
def decrypt(string): return KEY.decrypt(bytes(string, "utf-8")).decode()

colorama.init()
LType      = lambda x: colorama.Fore.GREEN         + x + colorama.Fore.RESET
LName      = lambda x: colorama.Fore.CYAN          + x + colorama.Fore.RESET
LVariable  = lambda x: colorama.Fore.MAGENTA       + x + colorama.Fore.RESET
LWarning   = lambda x: colorama.Fore.YELLOW        + x + colorama.Fore.RESET
LError     = lambda x: colorama.Fore.RED           + x + colorama.Fore.RESET
LSQLnames  = lambda x: colorama.Fore.LIGHTBLACK_EX + x + colorama.Fore.RESET
LSQLsyntax = lambda x: colorama.Fore.CYAN          + x + colorama.Fore.RESET
LSQLsymbol = lambda x: colorama.Fore.GREEN         + x + colorama.Fore.RESET
LSQLout    = lambda x: colorama.Fore.LIGHTBLACK_EX + x + colorama.Fore.RESET
CLink      = colorama.Fore.LIGHTBLACK_EX
CDebug     = colorama.Back.CYAN    + colorama.Fore.BLACK   + " ? " + colorama.Style.RESET_ALL
CValue     = colorama.Fore.BLACK   + colorama.Fore.CYAN    + " = " + colorama.Style.RESET_ALL
COut       = colorama.Back.BLACK   + colorama.Fore.CYAN    + " ? " + colorama.Style.RESET_ALL
CError     = colorama.Back.RED     + colorama.Fore.BLACK   + "!!!" + colorama.Style.RESET_ALL
CErrorUp   = colorama.Back.RED     + colorama.Fore.BLACK   + " ↑ " + colorama.Style.RESET_ALL
CErrorDown = colorama.Back.RED     + colorama.Fore.BLACK   + " ↓ " + colorama.Style.RESET_ALL
CWarning   = colorama.Back.YELLOW  + colorama.Fore.BLACK   + " ! " + colorama.Style.RESET_ALL
CSQL       = colorama.Back.MAGENTA + colorama.Fore.BLACK   + "SQL" + colorama.Style.RESET_ALL
CSQLout    = colorama.Back.BLACK   + colorama.Fore.MAGENTA + "sql" + colorama.Style.RESET_ALL
CIOreceive = colorama.Back.GREEN   + colorama.Fore.BLACK   + "SOC" + colorama.Style.RESET_ALL \
	+ colorama.Fore.GREEN + " receive" + colorama.Fore.RESET
CIOsend    = colorama.Back.GREEN   + colorama.Fore.BLACK   + "SOC" + colorama.Style.RESET_ALL \
	+ colorama.Fore.GREEN + "    send" + colorama.Fore.RESET
CReset     = colorama.Style.RESET_ALL




class ConnectionStatus:
	UnexceptedError  = -1
	Allright         =  0
	Unset            =  1
	InterfaceError   =  2
	OperationalError =  3
	ProgrammingError =  4




class debug_object (object):
	DEBUG = True
	DEEP_DEBUG = False

	def __getattribute__(self, name):
		result = object.__getattribute__(self, name)
		
		if object.__getattribute__(self, "DEBUG") and callable(result) and name[:1] != "_" and name != "debug":
			print(f"{CDebug} {LType(object.__getattribute__(self, '__class__').__name__)}.{LName(result.__name__)}() {CLink}File \"{result.__code__.co_filename}\", line {result.__code__.co_firstlineno}{CReset}")
		
		elif object.__getattribute__(self, "DEBUG") and object.__getattribute__(self, "DEEP_DEBUG"):
			print(f"{CValue} {LName(name)} = {result}")
		
		return result
	
	def debug(self, name):
		result = object.__getattribute__(self, name)
		print(f"{CValue} {LName(name)} = {result}")
	
	def out(*string):
		if DEBUG: print(f"{COut} {" ".join(tuple(map(str, string)))}")

	def value(name, result):
		if DEBUG: print(f"{CValue} {LName(name)} = {result}")
		
	def warning(*string):
		if DEBUG: print(f"{CWarning} {" ".join(tuple(map(str, string)))}")
	
	def error(*string):
		print(f"{CError} {LError(" ".join(tuple(map(str, string))))}")
	
	def sql(command):
		if not DEBUG: return
		
		for i in ["SELECT", "FROM", "ADD", "INSERT", "INTO", "VALUES", "WHERE", "UPDATE", "SET", "DELETE", "CREATE", "DROP", "TABLE", "DATABASE"]:
			command = command.replace(i, LSQLsyntax(i))
		for i in ["AND", "OR", "=", ">", "<", "(", ")", "*", "'", "\"", "%", ",", "."]:
			command = command.replace(i, LSQLsymbol(i))
		
		print(f"{CSQL} {command}")
	
	def sql_out(*string):
		if DEBUG: print(f"{CSQLout} {LSQLout(" ".join(tuple(map(str, string))))}")
	
	def socket_receive(*string):
		if DEBUG: print(f"{CIOreceive} {" ".join(tuple(map(str, string)))}")
	
	def socket_send(*string):
		if DEBUG: print(f"{CIOsend} {" ".join(tuple(map(str, string)))}")




class Flag:
	Default = 0,
	Encode = 1,
	Encrypt = 2

class Column (object):
	"""data_type:  int | str | bool
	flag:  Default | Encode | Encrypt"""

	def __init__(self, name: str, data_type: Callable, sql_type: str, flag=Flag.Default):
		self.name = name
		self.data_type = data_type
		self.sql_type = sql_type
		self.flag = flag
	
	def unconvert(self, value: Any):
		if self.flag == Flag.Encode:
			value = decode(value)
		elif self.flag == Flag.Encrypt:
			value = decrypt(value)
		
		return self.data_type.__call__(value)
	
	def convert(self, value: Any):
		if self.flag == Flag.Encode:
			value = encode(value)
		elif self.flag == Flag.Encrypt:
			value = encrypt(value)
		
		_type = int
		if "char" in self.sql_type:
			return f'{value}'
		return _type.__call__(value)
	
	def __repr__(self):
		return f"{self.name} {self.sql_type}"




class TableHead (object):
	def __init__(self, name: str, *columns: Column):
		self.name = name
		self.columns = columns
	
	def get_column(self, name):
		for col in self.columns:
			if col.name == name:
				return col
		return None
	
	def get_column_index(self, name):
		for i, col in enumerate(self.columns):
			if col.name == name:
				return i
		return None
	
	def get_column_names(self):
		return f"({", ".join([i.name for i in self.columns[1:]])})"
	
	def __repr__(self):
		return f"{self.name} ({", ".join([str(i) for i in self.columns])})"




class Handler (debug_object):
	def __init__(self, base):
		self.connection = base.get_connection()
		self.cursor = self.connection.cursor()
	
	def __enter__(self):
		return self

	def _WRITE(self, sql_command: str) -> int:
		"""Returns 0 if success, 1 if failed"""
		try:
			self.cursor.execute(sql_command)
			self.connection.commit()
			return 0
		except Exception as e:
			tupl = eval(str(e))
			error_id = tupl[0]
			text = tupl[1]
			
			while ("[" in text) and ("]" in text):
				text = text.replace(text[text.index("["):text.index("]")+1], "")
			while text[0] == " ":
				text = text[1:]
			
			debug_object.error(error_id, text)
			return 1
	
	def _EXECUTE(self, sql_command: str) -> int:
		"""Returns 0 - success, 1 - failed"""
		try:
			self.cursor.execute(sql_command)
			debug_object.sql(sql_command)
			return 0
		except Exception as e:
			debug_object.value("sql_command", sql_command)
			raise e
			return 1
	
	def _READ(self, sql_command: str) -> list[pyodbc.Row,]:
		try:
			self.cursor.execute(sql_command)
			return self.cursor.fetchall()
		except Exception as e:
			debug_object.value("sql_command", sql_command)
			raise e
			return 1
	
	def __exit__(self, exception_type, exception_value, traceback):
		return

	def __del__(self):
		del self.cursor
		self.connection.close()




class BaseHandler (Handler):
	def __init__(self, base):
		Handler.__init__(self, base)
		self.base = base

	def create_table(self, head: TableHead) -> None:
		"""Creates new table"""
		command = f"CREATE TABLE {head}"
		debug_object.sql(command)
		if not self._WRITE(command):
			self.base.tables.append(head.name)
			debug_object.sql_out("Success")
	
	def drop_table(self, name) -> None:
		"""Drop (delete) new table"""
		command = f"DROP TABLE {name}"
		debug_object.sql(command)
		if not self._WRITE(command):
			self.base.tables.pop(
				self.base.tables.index(head.name))
			debug_object.sql_out("Success")




class TableHandler (Handler):
	global DEBUG
	DEBUG = DEBUG

	def __init__(self, base, head: TableHead):
		super().__init__(base)
		self.name = head.name
		self.head = head
		
		debug_object.value("base.tables", base.tables)

		if self.name not in base.tables:
			with BaseHandler(base) as handler:
				handler.create_table(head)
		
	def _get_last_ID(self) -> int | None:
		return self._READ(f"SELECT max(ID) FROM {self.name}")[0][0]
	
	def get_rows(self, ID: int) -> list[list,]:
		"""Return list of rows by ID"""
		selector = f"SELECT * FROM {self.name} WHERE {self.head.columns[0].name} = {ID}"
		debug_object.sql(selector)
		finded = self._READ(selector)
		
		if len(finded) == 0:
			debug_object.sql_out(LWarning("Not found"))
			return []
		
		debug_object.sql_out("Founded:", len(finded))
		finded = [[self.head.columns[i].unconvert(value) for i, value in enumerate(row)] for row in finded]

		return finded
	
	def get_row(self, ID: int) -> list | None:
		"""Return single row by ID, if not find - None"""
		try:
			return self.get_rows(ID)[0]
		except:
			return None

	def get_by(self, find_column: str, find_value: Any) -> list[list,]:
		"""Return row by column value"""
		find_value = self.head.get_column(find_column).convert(find_value)
		selector = f"SELECT * FROM {self.name} WHERE {find_column} = {find_value.__repr__()}"
		debug_object.sql(selector)
		finded = self._READ(selector)

		if len(finded) == 0:
			debug_object.sql_out(LWarning("Not found"))
			return []
		
		debug_object.sql_out("Founded:", len(finded))
		finded = [[self.head.columns[i].unconvert(value) for i, value in enumerate(row)] for row in finded]

		return finded

	def get_where(self, where) -> list[Any,]:
		"""SELECT * FROM ... WHERE {where}
		Return row by selector"""
		selector = f"SELECT * FROM {self.name} WHERE {where}"
		debug_object.sql(selector)
		finded = self._READ(selector)

		if len(finded) == 0:
			debug_object.sql_out(LWarning("Not found"))
			return []
		
		debug_object.sql_out("Founded:", len(finded))
		finded = [[self.head.columns[i].unconvert(value) for i, value in enumerate(row)] for row in finded]

		return finded
		
	def add_row(self, *values: Any) -> int:
		"""Input new row without ID column
		Returns new row ID"""
		values = tuple([self.head.columns[i].convert(value) for i, value in enumerate(values, 1)])
		command = f"INSERT INTO {self.name} {self.head.get_column_names()} VALUES {values}"
		debug_object.sql(command)
		self._WRITE(command)
		last_ID = self._get_last_ID()
		debug_object.sql_out("Success")
		return last_ID
	
	def update(self, row_ID: int, column: str, value: Any) -> None:
		"""Update single value in column, by row ID"""
		column = str(column)
		value = self.head.get_column(column).convert(value)
		command = f"UPDATE {self.name} SET {column} = {value.__repr__()} WHERE {self.head.columns[0].name} = {row_ID}"
		debug_object.sql(command)
		self._WRITE(command)




class Base (debug_object):
	main_connection: pyodbc.Connection
	cursor: pyodbc.Cursor
	timeout = 2

	def __init__(self, database: str, driver="SQL Server", login="", password=""):
		global DEBUG
		self.DEBUG = DEBUG

		self.server = os.getenv("SQL_SERVER")
		self.database = database
		self.driver = driver
		self.login = login
		self.password = password
		self.update_request()
		self.connection_status = self.test_connection()
		self.debug("connection_status")

		if self.connection_status:
			debug_object.error("Fail to connect")
			return

		self.cursor = self.main_connection.cursor()
		self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
		self.tables = self._get_tables()
	
	def update_request(self):
		self.connection_request = \
			f"Driver={self.driver};" \
			f"Server={self.server};" \
			f"Database={self.database};" \
			f"UID={self.login};" \
			f"PWD={self.password};" \
			"trust_connection=yes;" \
			"encoding=utf-8;"
		self.debug("connection_request")
	
	def test_connection(self) -> ConnectionStatus:
		try:
			if not self.main_connection.closed():
				self.main_connection.close()
		except: None

		try:
			self.main_connection = pyodbc.connect(self.connection_request, timeout=self.timeout)
			return ConnectionStatus.Allright

		except Exception as Error:
			error_type = f"{Error.__module__}.{Error.__class__.__name__}"
			error_data = eval(Error.__str__())[1]
			errors_list = []

			for text in list(set(error_data.split(";"))):
				while ("[" in text) and ("]" in text):
					text = text.replace(text[text.index("["):text.index("]")+1], "")
				while text[0] == " ":
					text = text[1:]
				errors_list.append(text)
			
			print(f"{CErrorDown} {error_type}  " + f"\n{CErrorDown} {error_type}: ".join(errors_list) + f"\n{CError} SQL error")

			if isinstance(Error, pyodbc.InterfaceError):
				print(f"{CWarning} Avaliable drivers:\n{CWarning} - " + f"\n{CWarning} - ".join(pyodbc.drivers()))
				return ConnectionStatus.InterfaceError
			
			if isinstance(Error, pyodbc.OperationalError):
				print(f"{CWarning} Fail to connect to the server")
				return ConnectionStatus.OperationalError
			
			if isinstance(Error, pyodbc.ProgrammingError):
				print(f"{CWarning} Error in DataBase name or login failed")
				return ConnectionStatus.ProgrammingError

			return ConnectionStatus.UnexceptedError
	
	def get_connection(self) -> pyodbc.Connection:
		conn = pyodbc.connect(self.connection_request, timeout=self.timeout)
		debug_object.out(conn)
		return conn
	
	def _get_tables(self, key: str=None) -> str:
		if key == None:
			self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
			return [table[2] for table in self.cursor.fetchall()]
		self.cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME LIKE '{key}%'")
		return [table[2] for table in self.cursor.fetchall() if key in table[2]]
	
	def _drop_all_tables(self):
		self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
		
		for table in self.cursor.fetchall():
			self.cursor.execute(f"DROP TABLE {table[2]}")
		
		self.main_connection.commit()
		self.tables = []
		debug_object.value("tables", self._get_tables())
		print(f"{CWarning} {LWarning("Database reset")}")
		exit()
