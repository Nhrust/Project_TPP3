from random import randint
from cryptography.fernet import Fernet

from source.sql import *

UserNotFind = "User not founded"
WrongPass   = "Wrong password"

SQL_BIGINT_MAX_VALUE = 9223372036854775806 # константа
HASH_KEY = 7433494284023295923 # случайное число
def hash(password):
	a_bytes = str(password).encode("utf-8")
	a_number = int(a_bytes.hex(), 16)
	return (a_number * HASH_KEY) % SQL_BIGINT_MAX_VALUE




class Account (debug_object):

	def __init__(self, base: Base, login: str, password: int, sql_sync=True):
		self.chat_opened = False
		self.opened_chat = Chat(None, -1, -1, -1, -1)
		
		self.DEBUG = True
		
		self.login = login
		self.password = password
		self.name = "Untitled"
		self.age = 0
		self.gender = 0
		self.about = ''
		self.icon = "default_icon.png"
		self.theme = ''
		self.visible = 0
		
		if not sql_sync: return

		with TableHandler(base, AccountsManager.Head) as handle:
			self.ID = handle.add_row(self.login, self.password, self.name, self.age, self.gender, self.about, self.theme, self.visible)
			self.name = f"User-{self.ID}"
			handle.update(self.ID, "name", self.name)
	
	def update_on_base(self, base: Base):
		with TableHandler(base, AccountsManager.Head) as handle:
			handle.update(self.ID, "name",   self.name  )
			handle.update(self.ID, "age",    self.age   )
			handle.update(self.ID, "gender", self.gender)
			handle.update(self.ID, "about",  self.about )
			handle.update(self.ID, "theme",  self.theme )
	
	def get_opened_chat(self, base: Base):
		pass
		# return ChatPreview(base, self.ID, self.opened_chat)
	
	# not a method
	def load(base: Base, ID: int):
		pass
		# try:
		# 	return Account.unpack( base.table("users").get("id", ID)[0] )
		# except Exception as e:
		# 	print(f"!!! Fail to load user {ID}: {str(e)}")
		# 	raise e
	
	# not a method
	def unpack(base, response: list):
		new = Account(None, None, None, sql_sync=False)
		new.ID, new.login, new.password, new.name, new.age, new.gender, new.about, new.theme, new.visible = response
		return new

	def __repr__(self):
		return f"{self.icon},{self.name},{self.ID}"




class AccountsManager (debug_object):
	TableName = TABLE + "accaunts"
	Head = TableHead(TableName,
		Column("ID",       int, "int identity(0,1)",        Flag.Default),
		Column("login",    str, "varchar(32)",              Flag.Default),
		Column("password", int, "BIGINT",                   Flag.Default),
		Column("name",     str, "varchar(256)",             Flag.Encode ),
		Column("age",      int, "varchar(128)",             Flag.Encrypt),
		Column("gender",   int, "tinyint",                  Flag.Default),
		Column("about",    str, "varchar(1024) default ''", Flag.Encrypt),
		Column("theme",    str, "varchar(192)",             Flag.Default),
		Column("visible",  int, "tinyint",                  Flag.Default)
	)

	def __init__(self, base: Base):
		self.DEBUG = True
		
		self.base = base

	def try_to_login(self, login: str, password: str) -> Account | str:
		"""if success - returns Account
		if failed - error string"""
		if len(str(password)) < 4:
			return WrongPass

		with TableHandler(self.base, self.Head) as handle:
			finded = handle.get_by("login", login)

			if len(finded) == 0:
				return UserNotFind
			
			for response in finded:
				user_data = Account.unpack(self.base, response)
				if hash(password) == user_data.password or password == user_data.password: # !!! DEBUG ##################################
					return user_data
			
			return WrongPass

	def check_login(self, login: str) -> bool:
		"""Возвращает существующий ли аккаунт с указанным login"""
		with TableHandler(self.base, self.Head) as handle:
			return len(handle.get_by("login", login)) != 0
	
	def find(self, requester_id: int, request: str) -> list:
		with TableHandler(self.base, self.Head) as handle:
			raw_finded = handle.get_where("name LIKE '%" + encode(request) + "%'")
			
			if request.isdigit():
				raw_finded = handle.get_rows(int(request)) + raw_finded
			
			debug_object.value("raw_finded", raw_finded)

			finded = []
			
			for i in raw_finded:
				if i not in finded:
					finded.append(i)
			
			if len(finded) == 0:
				return []

			result = []
			for item in finded:
				acc = Account.unpack(self.base, item)
				if acc.ID == requester_id:
					continue
				result.append(acc)

			return result

	def add(self, login: str, password: str) -> Account:
		"""Создаёт аккаунт на базе и возвращает его"""
		return Account(self.base, login, hash(password))

	def delete(self, ID: int):
		pass
	
	def _debug_get_all(self):
		with TableHandler(self.base, self.Head) as handle:
			last_ID = handle._get_last_ID()
			result = []
			
			if last_ID != None:
				for i in range(last_ID + 1):
					result.append(Account.unpack(self.base, handle.get_row(i)))
			
			return result




class ClientManager:
	def __init__(self):
		self.clients = dict()

	def add(self, ip: int, account: Account) -> None:
		"""Добавляет нового клиента"""
		self.clients[ip] = account

	def remove(self, ip: int) -> None:
		"""Удаляет клиента с указанным ip (адресом)"""
		try:
			del self.clients[ip]
		except:
			None

	def get(self, ip: int) -> Account:
		"""Возвращает экземпляр Account по ip"""
		try:
			return self.clients[ip]
		except:
			return None

	def __getitem__(self, ip) -> Account:
		return self.get(ip)




class Message:
	Columns = [
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("sender",  int, "int",               Flag.Default),
		Column("data",    str, "varchar(1024)",     Flag.Encrypt),
		Column("time",    str, "varchar(14)",       Flag.Default),
		Column("visible", int, "tinyint",          Flag.Default)
	]

	def __init__(self, ID: int, sender: int, data: str, time: str, visible: int):
		self.ID = ID
		self.sender = sender
		self.data = data
		self.time = time
		self.deleted = deleted
	
	def pack(self) -> str:
		return f"{self.ID},{self.sender},{self.time},{self.deleted},{len(self.data)},{self.data}"

	# not a method
	def unpack(response: list):
		new = Message(None, None, None, None, None)
		response = [ChatManager.Head.columns[i].unconvert(value) for i, value in enumerate(row)]
		new.ID, new.sender, new.data, new.time, new.deleted = response
		return new




class Chat:
	def __init__(self, manager, ID: int, user1: int, user2: int, viewed_ID):
		self.manager = manager
		self.ID = ID
		self.user1_ID = viewed_ID
		self.user2_ID = user1 if user1 != viewed_ID else user2
		
		self.exist = False
		if self.manager == None: return
		with TableHandler(manager.base, AccountsManager.Head) as accaunts_handle, \
			TableHandler(manager.base, TableHead( CHAT + str(self.ID), *(Message.Columns) )) as chat_handle:
			self.user1 = Account.unpack(manager.base, accaunts_handle.get_row(self.user1_ID))
			self.user2 = Account.unpack(manager.base, accaunts_handle.get_row(self.user2_ID))

			last_message_ID = chat_handle._get_last_ID()
			self.show_last_message = last_message_ID != None
			if self.show_last_message:
				self.last_message = Message(chat_handle.get_row(last_message_ID))

			self.exist = True

		# finded_chats = base.table("chats").get("id", chat_id)
		# if base.DEBUG: print(f"? ChatPreview ? {finded_chats = }")
		
		# if len(finded_chats) == 0:
		# 	self.valid = False
		# 	return
		
		# chat = finded_chats[0]
		# self.valid = True
		# self.receiver_id = chat[1] if chat[1] != client_id else chat[2]
		# self.name = decode(base.table("users").get("id", self.receiver_id, "name")[0][0])
		# self.last_message_id = base.(CHAT + str(self.id))
		# self.icon = "default_icon.png"
	
	def get_message(self, ID: int):
		pass




class Group:
	""""""




class Band:
	Columns = [
		Column("user",   int, "int",          Flag.Default),
		Column("alias",  str, "varchar(256)", Flag.Encrypt),
		Column("rights", int, "tinyint",      Flag.Default)]




class Manager (debug_object):
	ChatsTableName = TABLE + "chats"
	ChatsHead = TableHead(ChatsTableName,
		Column("ID",    int, "int identity(0,1)"),
		Column("user1", int, "int"              ),
		Column("user2", int, "int"              ))
	
	GroupsTableName = TABLE + "groups"
	GroupsHead = TableHead(GroupsTableName,
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("band",    int, "int",               Flag.Default),
		Column("name",    str, "varchar(256)",      Flag.Encrypt),
		Column("visible", int, "tinyint",           Flag.Default))

	BandsTableName = TABLE + "bands"
	BandsHead = TableHead(BandsTableName,
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("visible", int, "tinyint",           Flag.Default))
	
	chats:  int # количество существующих личных чатов
	groups: int # количество существующих групповых чатов
	bands:  int # количество существующих банд

	def __init__(self, base: Base):
		self.base = base
		
		with BaseHandler(base) as base_handle:
			if self.ChatsTableName not in base.tables:
				base_handle.create_table(self.ChatsHead)
				self.chats = 0
			else:
				with TableHandler(base, self.ChatsHead) as chats_handle:
					last_ID = chats_handle._get_last_ID()
					self.chats = last_ID + 1 if last_ID != None else 0

			if self.GroupsTableName not in base.tables:
				base_handle.create_table(self.GroupsHead)
				self.groups = 0
			else:
				with TableHandler(base, self.ChatsHead) as groups_handle:
					last_ID = groups_handle._get_last_ID()
					self.groups = last_ID + 1 if last_ID != None else 0

			if self.BandsTableName not in base.tables:
				base_handle.create_table(self.BandsHead)
				self.bands = 0
			else:
				with TableHandler(base, self.BandsHead) as bands_handle:
					last_ID = bands_handle._get_last_ID()
					self.bands = last_ID + 1 if last_ID != None else 0
	
	def get_all_chats_for_user(self, accaunt_ID) -> list:
		with TableHandler(self.base, self.ChatsHead) as chats_handle: # TODO add bands
			finded = chats_handle.get_by("user1", accaunt_ID) + chats_handle.get_by("user2", accaunt_ID)
			result = [Chat(self, *row, accaunt_ID) for row in finded]

			# TODO add bands

			return result
	
	def get_chat(self, user1: int, user2: int) -> Chat:
		userMIN = min(user1, user2)
		userMAX = max(user1, user2)

		with TableHandler(self.base, self.ChatsHead) as handle:
			finded = handle.get_where(f"user1 = {userMIN} AND user2 = {userMAX}")

			if len(finded) == 0:
				new_chat_ID = handle.add_row(userMIN, userMAX)
				return Chat(self, new_chat_ID, userMIN, userMAX, user1)
			else:
				return Chat(self, *finded[0], user1)
