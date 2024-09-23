from time import gmtime, strftime
from random import randint
from classes import *

int64_max = 2 ** 31
HASH_KEY = 3920713911

UserNotFind = "User not founded"
WrongPass = "Wrong password"

def LOG(*args):
	f = open("logs.txt", "a")
	print(f"[{strftime('%H:%M:%S', gmtime())}]\n", *args, file=f)
	f.close()

def hash(string: str):
	integer = int( str(string).encode().hex(), 16 )
	return (integer * HASH_KEY) % int64_max

class AccountsManager:
	def __init__(self, base):
		self.base = base
		
		if "users" not in self.base.tables:
			self.base.create_table("users", "id int identity(0,1)", "login varchar(32)", "password int", "name varchar(32)", "age tinyint default 0", "gender tinyint default 0", "description varchar(180) default ''")

		self.base.commit()

	def get(self, login, password):
		finded = self.base["users"].get("login", login)
		if len(finded) == 0:
			return UserNotFind
		for response in finded:
			user_data = User.unpack(response)
			if hash(password) == user_data.password:
				return User.load(self.base, user_data.id)
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
		self.base.create_table("users", "id int identity(0,1)", "login varchar(32)", "password int")
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