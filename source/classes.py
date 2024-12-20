from prefs import *


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
		self.icon = "static/Images/default_icon.png"
		self.theme = "ddddddbbbbbb1f1f1f3f3f3f555555777777999999dddddd0f263d2d1e3d999999aaaaaa000000000000000000000000" + "0" * 96
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
			return UI_texts.WrongPass

		with TableHandler(self.base, self.Head) as handle:
			finded = handle.get_by("login", login)

			if len(finded) == 0:
				return UI_texts.UserNotFind
			
			for response in finded:
				user_data = Account.unpack(self.base, response)
				if hash(password) == user_data.password or password == user_data.password: # !!! DEBUG ##################################
					return user_data
			
			return UI_texts.WrongPass

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
		self.sids = dict()

	def add(self, ip: str, account: Account) -> None:
		"""Добавляет нового клиента"""
		self.clients[ip] = account
	
	def add_sid(self, ID: int, sid: str) -> None:
		self.sids[ID] = sid

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
	
	def get_sid(self, ID: int) -> str:
		try:
			return self.sids[ID]
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
		self.visible = visible
	
	def pack(self) -> str:
		return f"{self.ID},{self.sender},{self.time},{self.visible},{len(self.data)},{self.data}"

	# not a method
	def unpack(chat, response: list):
		new = Message(None, None, None, None, None)
		new.ID, new.sender, new.data, new.time, new.visible = response
		return new




class Chat:
	def __init__(self, manager, ID: int, user1: int, user2: int, viewed_ID) -> None:
		self.manager = manager
		self.ID = ID
		self.user1_ID = viewed_ID
		self.user2_ID = user1 if user1 != viewed_ID else user2
		self.Head = TableHead( CHAT + str(self.ID), *(Message.Columns) )
		
		self.exist = False
		if self.manager == None: return
		with TableHandler(manager.base, AccountsManager.Head) as accaunts_handle, \
			TableHandler(manager.base, self.Head) as chat_handle:

			self.user1 = Account.unpack(manager.base, accaunts_handle.get_row(self.user1_ID))
			self.user2 = Account.unpack(manager.base, accaunts_handle.get_row(self.user2_ID))

			last_message_ID = chat_handle._get_last_ID()
			self.show_last_message = last_message_ID != None
			if self.show_last_message:
				finded = chat_handle.get_row(last_message_ID)
				self.last_message = Message(*finded)

			self.exist = True
	
	def get_message(self, ID: int) -> Message | None:
		with TableHandler(self.manager.base, self.Head) as handle:
			finded = handle.get_row(int(ID))
			if finded == None:
				return None
			return Message.unpack(self, finded)
	
	def get_messages(self, start_ID: int, end_ID: int) -> list[Message,]:
		start_ID, end_ID = min(start_ID, end_ID), max(start_ID, end_ID)

		with TableHandler(self.manager.base, self.Head) as handle:
			finded = handle.get_where(f"ID >= {start_ID} AND ID <= {end_ID}")

			if len(finded) == 0:
				return []
			
			return [Message.unpack(self, i) for i in finded]
	
	def get_last_messages(self) -> list[Message,]:
		with TableHandler(self.manager.base, self.Head) as handle:
			last_ID = handle._get_last_ID()
			
			if last_ID == None:
				return []
			
			finded = handle.get_where(f"ID >= 0 AND ID <= {last_ID}")
			
			if len(finded) == 0:
				return []
			
			return [Message.unpack(self, i) for i in finded]
	
	def get_last_message_ID(self) -> int | None:
		with TableHandler(self.manager.base, self.Head) as handle:
			return handle._get_last_ID()




class Group:
	def __init__(self):
		pass




class Band:
	def __init__(self):
		pass




class Manager (debug_object):
	ChatsTableName = TABLE + "chats"
	ChatsHead = TableHead(ChatsTableName,
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("user1",   int, "int",               Flag.Default),
		Column("user2",   int, "int",               Flag.Default))
	
	GroupsTableName = TABLE + "groups"
	GroupsHead = TableHead(GroupsTableName,
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("band",    int, "int",               Flag.Default),
		Column("name",    str, "varchar(256)",      Flag.Encrypt),
		Column("visible", int, "tinyint",           Flag.Default))

	BandsTableName = TABLE + "bands"
	BandsHead = TableHead(BandsTableName,
		Column("ID",      int, "int identity(0,1)", Flag.Default),
		Column("user",    int, "int",               Flag.Default),
		Column("alias",   str, "varchar(256)",      Flag.Encrypt),
		Column("rights",  int, "tinyint",           Flag.Default),
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




def get_account() -> Account:
	ip = request.remote_addr
	return clients[ip]




accounts = AccountsManager(base)
clients = ClientManager()
manager = Manager(base)