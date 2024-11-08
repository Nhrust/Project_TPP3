from source.classes  import *
from source.pages    import *
from source.requests import *
from source.socket   import *


if not accounts.check_login("admin"):
	admin = Account(base, "admin", 2902063403365090132)
	admin.name = "Админ"
	admin.update_on_base(base)


app.run(debug=True, host="0.0.0.0")