from flask import *
from sql import *
from clients import  *

app = Flask(__name__)

base = SQL_base('ASUS', 'project')

base.show()

accounts = AccountsManager(base)
clients = ClientManager()

@app.route('/')
def home():
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)

