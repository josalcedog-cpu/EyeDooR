from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, db
import os
import re
import random
import string
import cv2

app = Flask(__name__)
app.secret_key = "ABCDE-FGHIJ-LMNOP"

cred = credentials.Certificate("eyedoor-firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://eyedoor-49c27-default-rtdb.firebaseio.com/'  
})

ref = db.reference("users")

CODE_REGEX = re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$')

def gen_code():
    def chunk():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{chunk()}-{chunk()}-{chunk()}"

def normalize_code(code):
    return code.strip().upper()

def valid_code_format(code):
    return bool(CODE_REGEX.match(code))

def get_user_by_email(email):
    users = ref.get() or {}
    for uid, data in users.items():
        if data.get("email") == email:
            data["id"] = uid
            return data
    return None

def create_user(email, password_hash, product_code):
    ref.push({
        "email": email,
        "password_hash": password_hash,
        "product_code": product_code
    })

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_email'] = user['email']
            session['product_code'] = user['product_code']
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('bienvenido'))
        else:
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        product_code_input = request.form.get('product_code', '').strip()

        if not email:
            flash("Ingresa un correo.", "error")
            return redirect(url_for('registro'))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for('registro'))

        if password != password2:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for('registro'))

        if get_user_by_email(email):
            flash("Ya existe una cuenta con ese correo.", "error")
            return redirect(url_for('registro'))

        product_code = "ABCDE-FGHIJ-KLMNO"

        password_hash = generate_password_hash(password)
        try:
            create_user(email, password_hash, product_code)
            flash("Cuenta creada exitosamente. Ahora puedes iniciar sesión.", "success")
        except Exception as e:
            flash("Error al crear el usuario: " + str(e), "error")
            return redirect(url_for('registro'))

        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

@app.route('/bienvenido')
def bienvenido():
    if 'user_email' not in session:
        flash("Debes iniciar sesión primero.", "error")
        return redirect(url_for('login'))

    email = session.get('user_email')
    code = session.get('product_code')
    return render_template('bienvenido.html', email=email, product_code=code)

# Se supone que estos botones deben funcionar
@app.route('/activar_microfono')
def activar_microfono():
    flash("🎙️ Micrófono activado (simulación).", "success")
    return redirect(url_for('bienvenido'))

@app.route('/capturar_foto')
def capturar_foto():
    try:
        # Se supone que esto crea la carpeta
        folder_path = "fotos_eyedoor"
        os.makedirs(folder_path, exist_ok=True)

        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()

        if ret:
            file_path = os.path.join(folder_path, "foto_capturada.jpg")
            cv2.imwrite(file_path, frame)
            flash(f"📸 Foto guardada correctamente en '{folder_path}'.", "success")
        else:
            flash("❌ No se pudo capturar la imagen.", "error")

        cam.release()
    except Exception as e:
        flash(f"Error al acceder a la cámara: {e}", "error")

    return redirect(url_for('bienvenido'))

@app.route('/_debug_list_users')
def debug_list_users():
    users = ref.get() or {}
    lista = []
    for uid, data in users.items():
        lista.append({"id": uid, "email": data.get("email"), "product_code": data.get("product_code")})
    return {"users": lista}

if __name__ == '__main__':
    app.run(debug=True)
