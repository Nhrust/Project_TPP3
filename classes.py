from time import gmtime, strftime

def LOG(*args):
	f = open("logs.txt", "a")
	print(f"[{strftime('%H:%M:%S', gmtime())}]\n", *args, file=f)
	f.close()

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
			LOG(f"!!! Fail to load user {index}")
	
	# not a method
	def unpack(response):
		new = User(None, None, None)
		new.id, new.login, new.password, new.name, new.age, new.gender, new.description = response
		return new

	def __repr__(self):
		return f"{self.index = }\n{self.login = }\n{self.password = }"