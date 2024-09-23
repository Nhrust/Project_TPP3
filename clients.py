from random import randint
from sql import SQL_base

int64_max = 2 ** 31
HASH_KEY = 3920713911

UserNotFind = "User not founded"
WrongPass = "Wrong password"

def hash(string: str):
	integer = int( str(string).encode().hex(), 16 )
	return (integer * HASH_KEY) % int64_max

class User:
	def __init__(self, index, login, password):
		self.index = index
		self.login = login
		self.password = password
		self.name = f"User-{self.index}"
		self.age = 0
		self.gender = 0
		self.description = ''

	def save(self):
		try:
			file = open(f"data/U{self.index}.dat", "w")
		except:
			print(f"!!! FAIL TO SAVE USER: {self.index}")
			print(f"!!!   fail to open: data/U{self.index}.dat\n")
			return
		print(self.__dict__, file=file)
		file.close()

	def load(index):
		try:
			file = open(f"data/U{index}.dat", "r")
		except:
			print(f"!!! FAIL TO LOAD USER: {index}")
			print(f"!!!   fail to open: data/U{index}.dat\n")
			return None
		new = User(None, None, None)
		new.__dict__ = eval(file.readline())
		return new

	def __repr__(self):
		return f"{self.index = }\n{self.login = }\n{self.password = }"
	
class UserData:
	def __init__(self, response):
		self.id, self.login, self.password, self.name, self.age, self.gender, self.description = response

class AccountsManager:
	def __init__(self, base: SQL_base):
		self.base = base
		
		if "users" not in self.base.tables:
			self.base.create_table("users", "id int identity(0,1)", "login varchar(32)", "password int", "name varchar(32)", "age tinyint default 0", "gender tinyint default 0", "description varchar(180) default ''")

		self.base.commit()

	def get(self, login, password):
		finded = self.base["users"].get("login", login)
		if len(finded) == 0:
			return UserNotFind
		for response in finded:
			user_data = UserData(response)
			if hash(password) == user_data.password:
				return User.load(user_data.id)
		return WrongPass

	def check_login(self, login):
		return len(self.base["users"].get("login", login))

	def add(self, login, password):
		self.base["users"].add(login, hash(password), params=("login", "password"))
		self.base.commit()
		index = self.base["users"].get("login", login)[0][0]
		new_user = User(index, login, hash(password))
		new_user.save()
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