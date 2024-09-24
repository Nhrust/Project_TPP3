from random import randint
from cryptography.fernet import Fernet
from sql import *

DEBUG = False
int64_max = 2 ** 31
HASH_KEY = 3920713911

KEY = Fernet(b'ja3SUk5zbKBMHy9IZZpogAysEX0O5g1UFLA_hgDmnnU=')
def encode(string): return str(string).encode().hex()
def decode(string): return bytearray.fromhex(string).decode()
def encrypt(string): return KEY.encrypt(str(string).encode()).decode()
def decrypt(string): return KEY.decrypt(bytes(string, "utf-8")).decode()

UserNotFind = "User not founded"
WrongPass = "Wrong password"

def hash(string: str):
	integer = int( str(string).encode().hex(), 16 )
	return (integer * HASH_KEY) % int64_max

class Account:
	def __init__(self, index, login, password):
		self.index = index
		self.login = login
		self.password = password
		self.name = f"User-{self.index}"
		self.age = 0
		self.gender = 0
		self.description = ''
	
	def create_on_base(self, base: SQL_base):
		base["users"].add(
			self.login, self.password, encode(self.name), self.age, self.gender, encrypt(self.description),
			params=("login", "password", "name", "age", "gender", "description"))
		self.index = base["users"].get("login", self.login)[0][0]
		self.name = f"User-{self.index}"
	
	def update_on_base(self, base):
		base["users"].set("id", self.index, "name", encode(self.name))
		base["users"].set("id", self.index, "age", self.age)
		base["users"].set("id", self.index, "gender", self.gender)
		base["users"].set("id", self.index, "description", encrypt(self.description))
	
	# not a method
	def load(base: SQL_base, index):
		try:
			return Account.unpack( base["users"].get("id", index)[0] )
		except Exception as e:
			print(f"!!! Fail to load user {index}: {str(e)}")
			raise e
	
	# not a method
	def unpack(response):
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
				"password int",
				"name varchar(256)",
				"age tinyint default 0",
				"gender tinyint default 0",
				"description varchar(1024) default ''")
			self.base.commit()

	def get(self, login, password):
		finded = self.base["users"].get("login", login)
		
		if DEBUG: print(finded)

		if len(finded) == 0:
			return UserNotFind
		for response in finded:
			user_data = Account.unpack(response)
			if hash(password) == user_data.password:
				return Account.load(self.base, user_data.index)
		return WrongPass

	def check_login(self, login) -> int:
		return len(self.base["users"].get("login", login))
	
	def find(self, response) -> list:
		return self.base["users"].get("id", int(response)) + self.base["users"].get("name", encode(response))

	def add(self, login, password) -> Account:
		new_user = Account("not init", login, hash(password))
		new_user.create_on_base(self.base)
		self.base.commit()
		return new_user

	def delete(self, index):
		self.base["users"].delete("id", index)
		self.base.commit()

	def reset(self):
		try:
			self.base.drop_table("users")
		except:
			None
		self.base.create_table("users",
			"id int identity(0,1)",
			"login varchar(32)",
			"password int",
			"name varchar(256)",
			"age tinyint default 0",
			"gender tinyint default 0",
			"description varchar(1024) default ''")
		self.base.commit()

class ClientManager:
	def __init__(self):
		self.clients = dict()

	def add(self, ip, user):
		self.clients[ip] = user

	def remove(self, ip):
		try:
			del self.clients[ip]
		except:
			return

	def get(self, ip):
		try:
			return self.clients[ip]
		except:
			return None

	def __getitem__(self, ip):
		return self.get(ip)

CHAT = "_CHT_"
GROUP_CHAT = "_GCH_"
GROUP_CHAT_USERS = "_GCU_"

class Message:
	def __init__(self, sender, data, time, deleted):
		self.sender = sender
		self.data = data
		self.time = time
		self.deleted = deleted
	
	# not a method
	def unpack(response):
		new = Message(None, None, None, None)
		new.sender, new.data, new.time, new.deleted = response
		return new

class Chat:
	def __init__(self, base: SQL_base, index):
		self.base = base
		finded = self.base["chats"].get("id", index)
		if len(finded) == 0:
			self.index, self.user1, self.user2 = self.base["chats"].get("id", index)[0]
			self.exist = True
		else:
			self.index, self.user1, self.user2 = index, None, None
			self.exist = False
	
	def get_message(self, id):
		if not self.exist:
			return Message(None, None, None, True)
		try:
			return self.base.GET(CHAT + str(self.index), "id", id)
		except:
			return Message(None, None, None, True)

class ChatManager:
	def __init__(self, base: SQL_base):
		self.base = base

		if "chats" not in self.base.tables:
			self.base.create_table("chats",
				"id int identity(0,1)",
				"user1 int",
				"user2 int")
			self.base.commit()
		
		if "group_chats" not in self.base.tables:
			self.base.create_table("group_chats",
				"id int identity(0,1)",
				"name varchar(256)",
				"type tinyint")
			self.base.commit()
	
	def create(self, user1, user2):
		self.base["chats"].add(user1, user2, params=("user1", "user2"))
		index = self.base["chats"].get_last_id()
		self.base.CREATE(CHAT + str(index),
			"sender int",
			"data varchar(1024)",
			"time varchar(14)",
			"deleted bit")
	
	def get_all_chats_for_user(self, user_id):
		return self.base["chats"].get("user1", user_id) + self.base["chats"].get("user2", user_id)