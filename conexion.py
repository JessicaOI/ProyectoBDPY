import pymongo

# Conectar a MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Seleccionar la base de datos
db = client["nombre_de_la_base_de_datos"]

# Seleccionar la colección
collection = db["nombre_de_la_coleccion"]

# Insertar un documento en la colección
document = {"name": "John Doe", "age": 25}
collection.insert_one(document)

# Buscar todos los documentos en la colección
documents = collection.find({})
for document in documents:
    print(document)
