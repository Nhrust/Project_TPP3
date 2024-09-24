from random import randint

int64_max = 2 ** 31
HASH_KEY = 3920713911

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
				"name varchar(32)",
				"age tinyint default 0",
				"gender tinyint default 0",
				"description varchar(180) default ''")
			self.base.commit()

	def get(self, login, password):
		finded = self.base["users"].get("login", login)
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
		self.base["users"].add(login, hash(password), params=("login", "password"))
		self.base.commit()
		index = self.base["users"].get("login", login)[0][0]
		new_user = User(index, login, hash(password))
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
			"name varchar(32)",
			"age tinyint default 0",
			"gender tinyint default 0",
			"description varchar(180) default ''")
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
	
	# not a method
	def load(base, index):
		try:
			return User.unpack( base["users"].get("id", index)[0] )
		except Exception as e:
			print(f"!!! Fail to load user {index}")
	
	# not a method
	def unpack(response):
		new = User(None, None, None)
		new.index, new.login, new.password, new.name, new.age, new.gender, new.description = response
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
				"name varchar(32)",
				"user1 int",
				"user2 int")
			self.base.commit()
		
		if "group_chats" not in self.base.tables:
			self.base.create_table("group_chats",
				"id int identity(0,1)",
				"name varchar(32)",
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