from flask import Flask, request, redirect, render_template, session
from pymongo import MongoClient


app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient("mongodb://localhost:27017/")
db = client["proyecto1"]
collectionUsers = db["users"]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['passwordLogin']
        print(email,password)
        user = collectionUsers.find_one({'email': email})
        if user and user['password'] == password:
            session['email'] = email
            return redirect('/welcome')
    return render_template('signupLogin.html')

@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form.get("gender")
        
        if not gender:
            return "You must select a gender option."
        
        collectionUsers.insert_one({'name': name, 'last_name': last_name,'email': email, 'password': password, 'gender': gender})
        return redirect('/welcome')
    return render_template('signupLogin.html')




@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

if __name__ == '__main__':
    app.run()
