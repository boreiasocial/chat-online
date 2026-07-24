from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat-online"

socketio = SocketIO(app, cors_allowed_origins="*")

usuarios = {}

# ---------------- BANCO ----------------

def conectar():
    return sqlite3.connect("chat.db")

def criar_banco():
    banco = conectar()

    banco.execute("""
    CREATE TABLE IF NOT EXISTS mensagens(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        autor TEXT,
        texto TEXT,
        hora TEXT
    )
    """)

    banco.commit()
    banco.close()

criar_banco()

# ---------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("entrar")
def entrar(nome):

    usuarios[request.sid] = nome

    emit("mensagem",{
        "autor":"Sistema",
        "texto":f"{nome} entrou."
    },broadcast=True)

    emit("usuarios",list(usuarios.values()),broadcast=True)

    banco = conectar()

    historico = banco.execute("""
        SELECT autor,texto,hora
        FROM mensagens
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    banco.close()

    historico.reverse()

    emit("historico",[
        {
            "autor":m[0],
            "texto":m[1],
            "hora":m[2]
        }
        for m in historico
    ])

@socketio.on("mensagem")
def mensagem(data):

    banco = conectar()

    banco.execute(
        "INSERT INTO mensagens(autor,texto,hora) VALUES(?,?,?)",
        (
            data["autor"],
            data["texto"],
            data["hora"]
        )
    )

    banco.commit()
    banco.close()

    emit("mensagem",data,broadcast=True)

@socketio.on("disconnect")
def sair():

    nome = usuarios.pop(request.sid,None)

    if nome:

        emit("mensagem",{
            "autor":"Sistema",
            "texto":f"{nome} saiu."
        },broadcast=True)

        emit("usuarios",list(usuarios.values()),broadcast=True)

if __name__=="__main__":
    socketio.run(app,host="0.0.0.0",port=10000)
