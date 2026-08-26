from flask import Flask, render_template, jsonify, request
from fields import FormRegistry
import database
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar Base de Datos al arrancar el servidor
try:
    print("Inicializando base de datos...")
    database.init_db()
except Exception as e:
    print(f"Error al inicializar la base de datos: {e}")
    print("La aplicación iniciará, pero las funciones de base de datos podrían fallar si no se configura .env")

@app.route('/')
def index():
    """Renderiza la página principal con la interfaz de usuario."""
    return render_template('index.html')

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Retorna el esquema dinámico del formulario en formato JSON."""
    fields = FormRegistry.get_fields()
    schema = [field.to_dict() for field in fields]
    return jsonify(schema)

@app.route('/api/register', methods=['POST'])
def register():
    """Procesa el registro del usuario con validación en el servidor."""
    data = request.json or {}
    
    # 1. Validar los datos recibidos usando el registro de campos dinámicos
    is_valid, errors = FormRegistry.validate_data(data)
    if not is_valid:
        return jsonify({
            "success": False,
            "message": "Error de validación en los datos ingresados.",
            "errors": errors
        }), 400
        
    # 2. Guardar el usuario en la base de datos
    success, message = database.save_user(data, FormRegistry.get_fields())
    if not success:
        return jsonify({
            "success": False,
            "message": message
        }), 400
        
    return jsonify({
        "success": True,
        "message": message
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Retorna la lista de todos los usuarios registrados."""
    users = database.get_all_users()
    return jsonify(users)

if __name__ == '__main__':
    # Ejecutar en modo desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)
