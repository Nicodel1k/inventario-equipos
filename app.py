from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="Admin",
        password="root",
        database="inventario"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form['username']
        clave = request.form['password']

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (usuario, clave))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario'] = user['username']
            return redirect('/')
        else:
            mensaje = '⚠️ Usuario o contraseña incorrectos'

    return render_template("login.html", mensaje=mensaje)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect('/login')

    filtro = request.args.get('buscar', '')
    campo = request.args.get('campo', 'tipo')  # por defecto filtra por tipo

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if filtro:
        if campo not in ['id', 'tipo', 'marca', 'modelo', 'serie', 'estado', 'ubicacion', 'responsable']:
            campo = 'tipo'  # seguridad

        if campo == 'id' and filtro.isdigit():
            cursor.execute(f"SELECT * FROM equipos WHERE id = %s", (filtro,))
        else:
            cursor.execute(f"SELECT * FROM equipos WHERE {campo} LIKE %s", (f"%{filtro}%",))
    else:
        cursor.execute("SELECT * FROM equipos")

    equipos = cursor.fetchall()
    conn.close()
    return render_template("index.html", equipos=equipos, buscar=filtro, campo=campo)


@app.route('/agregar', methods=["GET", "POST"])
def agregar():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == "POST":
        tipo = request.form['tipo']
        marca = request.form['marca']
        modelo = request.form['modelo']
        serie = request.form['serie']
        estado = request.form['estado']
        ubicacion = request.form['ubicacion']
        responsable = request.form['responsable']
        fecha_ingreso = request.form['fecha_ingreso'] or None
        fecha_egreso = request.form['fecha_egreso'] or None

        datos = (
            tipo, marca, modelo, serie, estado,
            ubicacion, responsable, fecha_ingreso, fecha_egreso
        )

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipos (tipo, marca, modelo, serie, estado, ubicacion, responsable, fecha_ingreso, fecha_egreso)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("formulario.html")


@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/editar/<int:id>', methods=["GET", "POST"])
def editar(id):
    if 'usuario' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        datos = (
            request.form['tipo'],
            request.form['marca'],
            request.form['modelo'],
            request.form['serie'],
            request.form['estado'],
            request.form['ubicacion'],
            request.form['responsable'],
            request.form['fecha_ingreso'] or None,
            request.form['fecha_egreso'] or None,
            id
        )
        cursor.execute("""
            UPDATE equipos
            SET tipo=%s, marca=%s, modelo=%s, serie=%s, estado=%s,
                ubicacion=%s, responsable=%s, fecha_ingreso=%s, fecha_egreso=%s
            WHERE id=%s
        """, datos)
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        cursor.execute("SELECT * FROM equipos WHERE id = %s", (id,))
        equipo = cursor.fetchone()
        conn.close()
        return render_template("editar.html", equipo=equipo)


if __name__ == '__main__':
    app.run(debug=True)
