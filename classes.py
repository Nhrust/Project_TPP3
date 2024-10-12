from random import randint
from cryptography.fernet import Fernet
from sql import *

DEBUG = True
int64_max = 2 ** 63
HASH_KEY = 2_178_561_987

KEY = Fernet(b'ja3SUk5zbKBMHy9IZZpogAysEX0O5g1UFLA_hgDmnnU=')
def encode(string): return str(string).encode().hex()
def decode(string): return bytearray.fromhex(str(string)).decode()
def encrypt(string): return KEY.encrypt(str(string).encode()).decode()
def decrypt(string): return KEY.decrypt(bytes(string, "utf-8")).decode()

UserNotFind = "User not founded"
WrongPass = "Wrong password"

def hash(string: str):
	integer = int( str(string).encode().hex(), 16 )
	print(integer)
	return (integer * HASH_KEY) % int64_max

class Account:
	chat_opened = False
	opened_chat = -1

	def __init__(self, index: int, login: str, password: int):
		self.index = index
		self.login = login
		self.password = password
		self.name = f"User-{self.index}"
		self.age = 0
		self.gender = 0
		self.description = ''
	
	def create_on_base(self, base: SQL_base):
		if base.DEBUG: print(f"> base.table('users').add({self.login}, {self.password}, encode({self.name}), {self.age}, {self.gender}, encrypt({self.description}), ...)")
		base.table("users").add(
			self.login, self.password, encode(self.name), self.age, self.gender, encrypt(self.description),
			params=("login", "password", "name", "age", "gender", "description"))
		base.commit()
		self.index = base.table("users").get_last_id()
		self.name = f"User-{self.index}"
		self.update_on_base(base)
	
	def update_on_base(self, base: SQL_base):
		base.table("users").set("id", self.index, "name", encode(self.name))
		base.table("users").set("id", self.index, "age", self.age)
		base.table("users").set("id", self.index, "gender", self.gender)
		base.table("users").set("id", self.index, "description", encrypt(self.description))
		base.commit()
	
	def get_opened_chat(self, base: SQL_base):
		return ChatPreview(base, self.index, self.opened_chat)
	
	# not a method
	def load(base: SQL_base, index: int):
		try:
			return Account.unpack( base.table("users").get("id", index)[0] )
		except Exception as e:
			print(f"!!! Fail to load user {index}: {str(e)}")
			raise e
	
	# not a method
	def unpack(response: list):
		if DEBUG: print("account unpack", response)
		new = Account(None, None, None)
		new.index, new.login, new.password, new.name, new.age, new.gender, new.description = response
		new.name = decode(new.name)
		new.description = decrypt(new.description)
		return new

	def __repr__(self):
		return f"{self.index = }\n{self.login = }\n{self.password = }"

class AccountsManager:
	def __init__(self, base: SQL_base):
		self.base = base

		if "users" not in self.base.tables:
			self.base.create_table("users",
				"id int identity(0,1)",
				"login varchar(32)",
				"password bigint",
				"name varchar(256)",
				"age tinyint default 0",
				"gender tinyint default 0",
				"description varchar(1024) default ''")
			self.base.commit()

	def get(self, login: str, password: str):
		if len(str(password)) < 4:
			return WrongPass

		finded = self.base.table("users").get("login", login)
		
		if DEBUG: print(finded)

		if len(finded) == 0:
			return UserNotFind
		for response in finded:
			user_data = Account.unpack(response)
			if hash(password) == user_data.password or password == user_data.password: # !!! DEBUG
				return Account.load(self.base, user_data.index)
		return WrongPass

	def check_login(self, login: str) -> int:
		return len(self.base.table("users").get("login", login))
	
	def find(self, requester_id: int, request: str) -> list:
		finded = self.base.table("users").get("name", "%" + encode(request) + "%", select_type="LIKE")
		
		if request.isdigit():
			finded = self.base.table("users").get("id", int(request)) + finded

		print("finded", finded)

		result = []
		for item in finded:
			if item[0] == requester_id:
				continue
			result.append( AccountPreview(Account.unpack(item)) )

		return result

	def add(self, login: str, password: str) -> Account:
		new_user = Account("not init", login, hash(password))
		new_user.create_on_base(self.base)
		self.base.commit()
		return new_user

	def delete(self, index: int):
		self.base.table("users").delete("id", index)
		self.base.commit()

	def reset(self):
		try:
			self.base.drop_table("users")
		except:
			None
		self.base.create_table("users",
			"id int identity(0,1)",
			"login varchar(32)",
			"password bigint",
			"name varchar(256)",
			"age tinyint default 0",
			"gender tinyint default 0",
			"description varchar(1024) default ''")
		self.base.commit()
	
	def get_all(self):
		last_id = self.base.table("users").get_last_id()
		result = []

		for i in range(last_id + 1):
			acc = Account.unpack(self.base.table("users").get("id", i)[0])
			result.append( (acc.login, acc.name) )
		
		if self.base.DEBUG: print(f"? classes.AccountsManager.get_all ? {result = }")
		
		return result

class ClientManager:
	def __init__(self):
		self.clients = dict()

	def add(self, ip: int, account: Account):
		self.clients[ip] = account

	def remove(self, ip: int):
		try:
			del self.clients[ip]
		except:
			return

	def get(self, ip: int) -> Account:
		try:
			return self.clients[ip]
		except:
			return None

	def __getitem__(self, ip) -> Account:
		return self.get(ip)

class Message:
	def __init__(self, sender: int, data: str, time: str, deleted: bool):
		self.sender = sender
		self.data = data
		self.time = time
		self.deleted = deleted
	
	# not a method
	def unpack(response: list):
		new = Message(None, None, None, None)
		new.sender, new.data, new.time, new.deleted = response
		return new

class ChatManager: None

class Chat:
	def __init__(self, manager: ChatManager, index: int):
		self.manager = manager
		finded = self.manager.base.table("chats").get("id", index)
		if len(finded) == 0:
			self.index, self.user1, self.user2 = finded[0]
			self.exist = True
		else:
			self.index, self.user1, self.user2 = index, None, None
			self.exist = False
	
	def get_message(self, id: int):
		if not self.exist:
			return Message(None, None, None, True)
		try:
			finded = self.manager.base.GET(CHAT + str(self.index), f"id = {id}")
			return Message( *(finded[0]) )
		except:
			return Message(None, None, None, True)
	
	def send_message(self, account: Account, raw_message: str):
		if self.exist:
			print("!!! CANNOT SEND MESSAGE BECAUSE CHAT NOT EXIST")
			return
		self.manager.base.ADD(CHAT + str(account.opened_chat), (encode(raw_message), "000000", 0), params=("data", "time", "deleted"))

class ChatPreview:
	def __init__(self, base: SQL_base, viever_id: int, chat_id: int):
		self.viever_id = viever_id
		self.chat_id = chat_id

		finded_chats = base.table("chats").get("id", chat_id)
		if base.DEBUG: print(f"? ChatPreview ? {finded_chats = }")
		
		if len(finded_chats) == 0:
			self.valid             = False
			self.receiver_id       = None
			self.name              = None
			self.show_last_message = None
			self.last_message      = None
			self.icon              = None
			return
		
		chat = finded_chats[0]
		self.valid = True
		self.receiver_id = chat[1] if chat[1] != viever_id else chat[2]
		self.name = decode(base.table("users").get("id", self.receiver_id, "name")[0][0])
		self.show_last_message = False
		self.last_message = "Error in ChatPreview"
		self.icon = "default_icon.png"

class AccountPreview:
	def __init__(self, account: Account):
		self.icon = "default_icon.png"
		self.name = account.name
		self.id = account.index
	
	def __repr__(self) -> str:
		return f"{self.icon},{self.name},{self.id}"

class ChatManager:
	chats_args = ["id int identity(0,1)", "user1 int", "user2 int"]
	group_chats_args = ["id int identity(0,1)", "name varchar(256)", "type tinyint"]


	def __init__(self, base: SQL_base):
		self.base = base

		if "chats" not in self.base.tables:
			self.base.create_table("chats", *self.chats_args)
			self.base.commit()
			self.chats = dict()
		else:
			self.chats = dict()
			for chat_name in self.base.get_tables_by_key(CHAT):
				chat_id = int(chat_name.replace(CHAT, ""))
				self.chats[chat_id] = Chat(self, chat_id)
		
		if "group_chats" not in self.base.tables:
			self.base.create_table("group_chats", *self.group_chats_args)
			self.base.commit()
		
	def get(self, user_id_1: int, user_id_2: int) -> int:
		user_id_1, user_id_2 = sorted((user_id_1, user_id_2))

		finded_chats: list = self.base.table("chats").GET(f"user1 = {user_id_1} AND user2 = {user_id_2}", "id")

		if len(finded_chats) == 0:
			self.create(user_id_1, user_id_2)
			return self.base.table("chats").get_last_id()
		
		return finded_chats[0][0]
	
	def get_second(self, chat_id, user_id) -> int:
		chat = self.base.table("chats").get("id", chat_id)[0]
		return chat[1] if user_id == chat[2] else chat[2]
	
	def create(self, user_id_1: int, user_id_2: int) -> None:
		if user_id_1 == user_id_2:
			print("!!! CANNOT CREATE CHAT: Users id equal", user_id_1)

		self.base.table("chats").add(min(user_id_1, user_id_2), max(user_id_1, user_id_2), params=("user1", "user2"))
		self.base.commit()
		index = self.base.table("chats").get_last_id()
		self.base.CREATE(CHAT + str(index),
			"sender int",
			"data varchar(1024)",
			"time varchar(14)",
			"deleted bit")
		self.base.commit()
		self.chats[index] = Chat(self, index)
	
	def get_all_chats_for_user(self, user_id) -> list:
		finded = self.base.table("chats").get("user1", user_id, "id") + self.base.table("chats").get("user2", user_id, "id")
		return [i[0] for i in finded]
	
	def __getitem__(self, index) -> Chat:
		try:
			return self.chats[index]
		except:
			return None