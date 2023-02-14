from flask import Flask, request, redirect, render_template, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MongoClient("mongodb+srv://proyecto:btstustatas@cluster0.xunnbo9.mongodb.net/test")
db = client["proyecto1"]
collectionUsers = db["users"]
collectionPosts = db["Posts"]
collectionRooms = db["Rooms"]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['passwordLogin']
        
        user = collectionUsers.find_one({'email.prymary': email})
        if user and user['password'] == password:
            session['email.prymary'] = email
            print(email,password)
            return redirect('/welcome')
    return render_template('signupLogin.html')

#registro
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        email2 = request.form['email2']
        password = request.form['password']
        country = request.form['country']
        gender = request.form.get("gender")
        
        # Define la estructura del nuevo subdocumento
        sub_document = {
            "prymary": email,
            "secundary": email2
        }
        main_document = {
            'name': name,
            'last_name': last_name,
            "email": sub_document,
            'password': password,
            'country': country,
            'gender': gender
        }
        if not gender:
            return "You must select a gender option."
        
        collectionUsers.insert_one(main_document)
        session['email.prymary'] = email
        return redirect('/welcome')
    return render_template('signupLogin.html')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    email = session.get('email.prymary')
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


@app.route('/proyecciones', methods=['GET', 'POST'])
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

    pipeline3 = [
    { "$match": { "gender": "Female" } },
    { "$count": "total_count" }
    ]

    pipeline4 = [
        { "$match": { "gender": "Male" } },
        { "$count": "total_count" }
    ]
    
    p1 = list(collection.aggregate(pipeline3))
    p2 = list(collection.aggregate(pipeline4))
    
    # Obtener la cantidad de personas que se están mostrando
    count_f = p1[0]["total_count"] if p1 else 0
    count_m = p2[0]["total_count"] if p2 else 0

    
    if request.method == 'POST':
        if request.form.get('submit_button') == 'Home':
            return redirect('/welcome')

    return render_template('proyecciones.html', proyecciones_f=proyecciones_f, proyecciones_m=proyecciones_m, count_f=count_f, count_m=count_m)

@app.route('/Room', methods=['GET', 'POST'])
def Room():
    email = session.get('email.prymary')
    
    # Obtener la instancia de la colección de usuarios
    collection = collectionUsers
    
    user_doc = collection.find_one({"email.prymary": email})
    friend_ids = user_doc.get("friends", [])
    friends = []
    
    for friend_id in friend_ids:
        friend = collection.find_one({"_id": friend_id})
        if friend:
            friends.append(friend['name'] + ' ' + friend['last_name'])
    
    if request.method == 'POST':
        if request.form.get('submit_button') == 'Enviar':
            # Obtener la lista de amigos seleccionados
            selected_friends = request.form.getlist('selected_friends')
            
            # Obtener los IDs de los amigos seleccionados
            friend_ids_selected = []
            for friend_name in selected_friends:
                first_name, last_name = friend_name.split()
                friend = collection.find_one({"name": first_name, "last_name": last_name})
                if friend:
                    friend_ids_selected.append(friend['_id'])
            
            # Crear una nueva sala de chat con el usuario actual como creador y los amigos seleccionados como participantes
            if friend_ids_selected:
                room_collection = collectionRooms
                room_collection.insert_many([{"creator": user_doc['_id'], "participants": friend_ids_selected}])

            # Redirigir al usuario a la página principal
            return redirect('/Room')
        elif request.form.get('submit_button') == 'Home':
            return redirect('/welcome')
        elif request.form.get('submit_button') == 'Chats':
            return redirect('/Chats')
    
    # Renderizar la plantilla HTML con la lista de amigos
    return render_template('room.html', friends=friends)


@app.route('/Chats', methods=['GET', 'POST'])
def Chats():
    # Obtener el correo electrónico del usuario actual
    email = session.get('email.prymary')

    # Obtener la instancia de la colección de usuarios
    collection = collectionUsers

    # Obtener el documento del usuario actual
    user_doc = collection.find_one({"email.prymary": email})

    # Obtener la instancia de la colección de salas de chat
    room_collection = collectionRooms

    # Obtener todas las salas de chat en las que el usuario actual es un participante o el creador
    rooms = room_collection.find({"$or": [{"creator": user_doc['_id']}, {"participants": user_doc['_id']}]})

    # Crear una lista de diccionarios con la información de cada sala de chat
    room_info = []
    for room in rooms:
        # Obtener el nombre y apellido del creador de la sala de chat
        creator_doc = collection.find_one({"_id": room['creator']})
        creator_name = creator_doc['name'] + ' ' + creator_doc['last_name']
        
        # Obtener los nombres y apellidos de los participantes de la sala de chat
        participant_names = []
        for participant_id in room['participants']:
            participant_doc = collection.find_one({"_id": participant_id})
            participant_name = participant_doc['name'] + ' ' + participant_doc['last_name']
            participant_names.append(participant_name)
        
        # Crear un diccionario con la información de la sala de chat y agregarlo a la lista de salas
        room_dict = {
            '_id': room['_id'],
            'creator_name': creator_name,
            'participant_names': participant_names
        }
        room_info.append(room_dict)
        
        if request.method == 'POST':
            if request.form.get('submit_button') == 'Home':
                return redirect('/welcome')

    # Renderizar la plantilla con la información de las salas de chat
    return render_template('chats.html', room_info=room_info)

@app.route('/logout')
def logout():
    session.pop('email.prymary', None)
    return redirect('/')

@app.route('/changePass', methods=['POST'])
def changePass():
    email = session.get('email.prymary')
    current_password = request.form['current_password']
    new_password = request.form['new_password']

    user = collectionUsers.find_one({'email.prymary': email})
    if user and user['password'] == current_password:
        collectionUsers.update_one({'_id': ObjectId(user['_id'])}, {'$set': {'password': new_password}})
        flash('Contraseña cambiada con éxito')
        return redirect('/welcome')
    else:
        flash('Contraseña actual incorrecta')
        return redirect('/changePass')


@app.route('/deleteUser')
def deleteUser():
    email = session.get('email.prymary')
     # Eliminar el documento correspondiente al correo electrónico especificado
    collectionUsers.delete_one({"email": email})
    session.pop('email.prymary', None)
    return redirect('/')

@app.route('/charts', methods=['GET', 'POST'])
def charts():
    return render_template('chartshtml.html')


if __name__ == '__main__':
    app.run()
