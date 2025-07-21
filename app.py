from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="Admin",
        password="root",
        database="inventario"
    )

@app.route('/')
def index():
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
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/editar/<int:id>', methods=["GET", "POST"])
def editar(id):
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
