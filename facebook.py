from flask import Flask, request, redirect, render_template, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient("mongodb://localhost:27017/")
db = client["proyecto1"]
collectionUsers = db["users"]
collectionPosts = db["Posts"]


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
        
        collectionUsers.insert_one({'name': name, 'last_name': last_name,'email': email, 'password': password, 'gender': gender,})
        session['email'] = email
        return redirect('/welcome')
    return render_template('signupLogin.html')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    email = session.get('email')
    if request.method == "POST":
        if "like_post" in request.form:
            post_id = request.form["like_post"]
            collectionPosts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes": 1}})
            flash("¡Like agregado!")
        else:
            publicacion = request.form['texto']
            insertar = {
                "autor": email,
                "post" : publicacion,
                "likes" : 0
            }
            collectionPosts.insert_one(insertar)
            flash("Publicacion con éxito!")
    # Obtener los posts ordenados por likes
    posts = collectionPosts.find().sort("likes", -1)
    return render_template('welcome.html', usuario=email, posts=posts)


@app.route('/proyecciones')
def proyecciones():
    # Obtener una instancia del objeto Collection
    collection = collectionUsers

    # Definir el pipeline de agregación
    pipeline = [
        { "$match": { "gender": "Female" } },
        { "$lookup": {
            "from": "users",
            "localField": "friends",
            "foreignField": "_id",
            "as": "friends_info"
        }},
        { "$project": { "name": 1, "gender": 1, "friends_info.email": 1 } }
    ]
    pipeline2 = [
        { "$match": { "gender": "Male" } },
        { "$lookup": {
            "from": "users",
            "localField": "friends",
            "foreignField": "_id",
            "as": "friends_info"
        }},
        { "$project": { "name": 1, "gender": 1, "friends_info.email": 1 } }
    ]

    # Ejecutar la consulta de agregación y obtener los resultados
    proyecciones_f = list(collection.aggregate(pipeline))
    proyecciones_m = list(collection.aggregate(pipeline2))

    # Obtener la cantidad de personas que se están mostrando
    count_f = len(proyecciones_f)
    count_m = len(proyecciones_m)

    return render_template('proyecciones.html', proyecciones_f=proyecciones_f, proyecciones_m=proyecciones_m, count_f=count_f, count_m=count_m)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

@app.route('/changePass')
def changePass():
    email = session.get('email')
    return render_template('changePass.html', email=email)

@app.route('/deleteUser')
def deleteUser():
    email = session.get('email')
     # Eliminar el documento correspondiente al correo electrónico especificado
    collectionUsers.delete_one({"email": email})
    session.pop('email', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
