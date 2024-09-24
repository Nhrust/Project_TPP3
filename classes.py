from random import randint
from cryptography.fernet import Fernet

DEBUG = False
int64_max = 2 ** 31
HASH_KEY = 3920713911

KEY = Fernet(b'ja3SUk5zbKBMHy9IZZpogAysEX0O5g1UFLA_hgDmnnU=')
def encrypt(string): return KEY.encrypt(str(string).encode()).decode()
def decrypt(string): return KEY.decrypt(bytes(string, "utf-8")).decode()

UserNotFind = "User not founded"
WrongPass = "Wrong password"

def hash(string: str):
	integer = int( str(string).encode().hex(), 16 )
	return (integer * HASH_KEY) % int64_max

class AccountsManager:
	def __init__(self, base):
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
			user_data = User.unpack(response)
			if hash(password) == user_data.password:
				return User.load(self.base, user_data.index)
		return WrongPass

	def check_login(self, login):
		return len(self.base["users"].get("login", login))

	def add(self, login, password):
		new_user = User("not init", login, hash(password))
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
	
class User:
	def __init__(self, index, login, password):
		self.index = index
		self.login = login
		self.password = password
		self.name = f"User-{self.index}"
		self.age = 0
		self.gender = 0
		self.description = ''
	
	def create_on_base(self, base):
		base["users"].add(
			self.login, self.password, encrypt(self.name), self.age, self.gender, encrypt(self.description),
			params=("login", "password", "name", "age", "gender", "description"))
		self.index = base["users"].get("login", self.login)[0][0]
		self.name = f"User-{self.index}"
	
	def update_on_base(self, base):
		base["users"].set("id", self.index, "name", encrypt(self.name))
		base["users"].set("id", self.index, "age", self.age)
		base["users"].set("id", self.index, "gender", self.gender)
		base["users"].set("id", self.index, "description", encrypt(self.description))
	
	# not a method
	def load(base, index):
		try:
			return User.unpack( base["users"].get("id", index)[0] )
		except Exception as e:
			print(f"!!! Fail to load user {index}: {str(e)}")
			raise e
	
	# not a method
	def unpack(response):
		new = User(None, None, None)
		if DEBUG: print(response)
		new.index, new.login, new.password, new.name, new.age, new.gender, new.description = response
		new.name = decrypt(new.name)
		new.description = decrypt(new.description)
		return new

	def __repr__(self):
		return f"{self.index = }\n{self.login = }\n{self.password = }"

CHAT = "_CHAT_"
GROUP_CHAT = "_GROUP_CHAT_"
GROUP_CHAT_USERS = "_CHAT_USERS_"

class ChatManager:
	def __init__(self, base):
		self.base = base

		self.chats = [i for i in self.base.get_tables_by_key("_CHAT_")]

		if "chats" not in self.base.tables:
			self.base.create_table("chats",
				"id int identity(0,1)",
				"name nvarchar(256)",
				"user1 int",
				"user2 int")
			self.base.commit()
		
		if "group_chats" not in self.base.tables:
			self.base.create_table("group_chats",
				"id int identity(0,1)",
				"name nvarchar(256)",
				"type tinyint")
	
	def get_view(self, chat_id, user_id):
		return []
	
	def get_chat_by_id(self, index):
		return Chat(base, index)

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
	def __init__(self, base, index):
		self.base = base
		try:
			self.index, self.name, self.user1, self.user2 = self.base["chats"].get("id", index)[0]
			self.exist = True
		except:
			self.index, self.name, self.user1, self.user2 = index, "Удалённый чат", None, None
			self.exist = False
	
	def get_message(self, id):
		if not self.exist:
			return Message(None, None, None, True)
		try:
			return self.base.GET(CHAT + str(self.index), "id", id)
		except:
			return Message(None, None, None, True)