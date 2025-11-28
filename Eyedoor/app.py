from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, db
import os
import re
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ABCDE-FGHIJ-LMNOP"

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

try:
    cred = credentials.Certificate("eyedoor-firebase.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://eyedoor-49c27-default-rtdb.firebaseio.com/'
    })
except Exception as e:
    print("ERROR INICIANDO FIREBASE:", e)

ref = db.reference("users")

CODE_REGEX = re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$')

VALID_PRODUCT_CODES = {
    "ABCDE-FGHIJ-KLMNO",
    "AAAAA-BBBBB-CCCCC",
    "FFFFF-GGGGG-HHHHH",
    "12345-ABCDE-99999"
}

def get_user_by_email(email):
    try:
        users = ref.get() or {}
        for uid, data in users.items():
            if data.get("email") == email:
                data["id"] = uid
                return data
    except Exception as e:
        print("ERROR LEYENDO USUARIO:", e)
    return None

def is_product_code_used(product_code):
    try:
        users = ref.get() or {}
        for uid, data in users.items():
            if data.get("product_code") == product_code:
                return True
    except Exception as e:
        print("ERROR LEYENDO CÓDIGOS DE PRODUCTO:", e)
    return False

def create_user(email, password_hash, product_code, question, answer_hash):
    try:
        ref.push({
            "email": email,
            "password_hash": password_hash,
            "product_code": product_code,
            "security_question": question,
            "security_answer_hash": answer_hash
        })
    except Exception as e:
        print("ERROR CREANDO USUARIO:", e)
        raise

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('bienvenido'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        try:
            user = get_user_by_email(email)
            if user and check_password_hash(user['password_hash'], password):
                session['user_email'] = user['email']
                session['product_code'] = user['product_code']
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for('bienvenido'))
        except Exception as e:
            print("ERROR EN LOGIN:", e)

        flash("Correo o contraseña incorrectos.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'user_email' in session:
        return redirect(url_for('bienvenido'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            password2 = request.form.get('password2', '')
            product_code = request.form.get('product_code', '').strip().upper()

            if product_code not in VALID_PRODUCT_CODES:
                flash("El código de producto no es válido.", "error")
                return redirect(url_for('registro'))

            if is_product_code_used(product_code):
                flash("Este código de producto ya está en uso.", "error")
                return redirect(url_for('registro'))

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

            security_question = request.form.get("security_question", "").strip()
            security_answer = request.form.get("security_answer", "").strip().lower()

            answer_hash = generate_password_hash(security_answer)
            password_hash = generate_password_hash(password)

            create_user(email, password_hash, product_code, security_question, answer_hash)
            flash("Cuenta creada exitosamente. Ahora puedes iniciar sesión.", "success")

        except Exception as e:
            flash("Error al crear el usuario: " + str(e), "error")
            return redirect(url_for('registro'))

        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if 'user_email' in session:
        return redirect(url_for('bienvenido'))

    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip().lower()
            user = get_user_by_email(email)

            if not user:
                flash("No existe un usuario con ese correo.", "error")
                return redirect(url_for("recuperar"))

            if "respuesta" not in request.form:
                pregunta = user.get("security_question", None)
                return render_template("recuperar.html", pregunta=pregunta, email=email)

            respuesta = request.form.get("respuesta", "").strip().lower()
            nueva_pass = request.form.get("nueva_pass", "").strip()

            if not check_password_hash(user.get("security_answer_hash", ""), respuesta):
                flash("La respuesta es incorrecta.", "error")
                return redirect(url_for("recuperar"))

            new_hash = generate_password_hash(nueva_pass)
            db.reference(f"users/{user['id']}/password_hash").set(new_hash)

            flash("Contraseña cambiada exitosamente.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash("Error durante el proceso: " + str(e), "error")

    return render_template("recuperar.html", pregunta=None)

@app.route('/bienvenido')
def bienvenido():
    if 'user_email' not in session:
        flash("Debes iniciar sesión primero.", "error")
        return redirect(url_for('login'))

    return render_template(
        'bienvenido.html',
        email=session.get('user_email'),
        product_code=session.get('product_code')
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

FOLDER = "fotos_eyedoor"
os.makedirs(FOLDER, exist_ok=True)
CAMERA_CAPTURE_URL = "http://10.90.173.123:81/capture"

@app.route("/capturar", methods=["GET"])
def capturar_foto():
    print("\n--- INICIANDO DIAGNÓSTICO DE CAPTURA ---")
    try:
        # 1. Verificar URL
        print(f"1. Conectando a la cámara en: {CAMERA_CAPTURE_URL}")
        response = requests.get(CAMERA_CAPTURE_URL, timeout=15)

        print(f"2. Respuesta recibida del ESP32.")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('Content-Type')}")
        print(f"   - Tamaño de datos: {len(response.content)} bytes")

        if response.status_code == 200 and response.content:
            filename = datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".jpg"
            filepath = os.path.join(FOLDER, filename)

            # 2. Intentar guardar archivo
            try:
                print(f"3. Intentando guardar archivo en: {filepath}")
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print("   ✅ Archivo guardado correctamente en disco.")
            except Exception as e:
                print(f"   ❌ ERROR CRÍTICO GUARDANDO ARCHIVO: {e}")
                return jsonify({"success": False, "error": f"Error de disco: {str(e)}"}), 500

            # 3. Intentar subir a Firebase
            try:
                print("4. Intentando subir a Firebase...")
                db.reference("fotos_eyedoor").push({
                    "file": filename,
                    "timestamp": datetime.now().isoformat(),
                    "uploader": session.get("user_email", "unknown")
                })
                print("   ✅ Subida a Firebase exitosa.")
            except Exception as e:
                print(f"   ⚠️ ERROR EN FIREBASE (No crítico): {e}")
                # No detenemos el proceso si falla Firebase, solo avisamos

            return jsonify({"success": True, "file": filename, "origen": "ESP32"}), 200

        else:
            print("❌ ERROR: El ESP32 respondió, pero con error o sin datos.")
            return jsonify({"success": False, "error": "ESP32 no devolvió imagen válida."}), 500

    except Exception as e:
        print(f"❌ EXCEPCIÓN CRÍTICA EN APP.PY: {e}")
        import traceback
        traceback.print_exc() # Esto imprimirá el error exacto
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

@app.route('/subir_estado')
def subir_estado():
    try:
        db.reference("estado_camara").set({
            "estado": "boton presionado",
            "mensaje": "Botón presionado = cámara activada"
        })
        flash("🔄 Estado enviado a Firebase Realtime Database.", "success")
    except Exception as e:
        flash(f"Error al subir estado: {e}", "error")

    return redirect(url_for('bienvenido'))

@app.route('/_debug_list_users')
def debug_list_users():
    try:
        users = ref.get() or {}
        lista = [{"id": uid, "email": d.get("email"), "product_code": d.get("product_code")} for uid, d in users.items()]
        return {"users": lista}
    except:
        return {"error": "No se pudieron listar los usuarios"}

if __name__ == '__main__':
    app.run(debug=True)
