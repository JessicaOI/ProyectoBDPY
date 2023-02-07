from flask import Flask, request, redirect, render_template, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["users"]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usernameLogin']
        password = request.form['passwordLogin']
        user = collection.find_one({'usernameLogin': username})
        if user and user['passwordLogin'] == password:
            session['usernameLogin'] = username
            return redirect('/welcome')
    return render_template('signupLogin.html')

@app.route('/', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/welcome')
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            collection.insert_one({'username': username, 'password': password})
            return redirect('/login')
    return render_template('signupLogin.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run()
