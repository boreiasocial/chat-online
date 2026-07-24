from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat-online"

socketio = SocketIO(app, cors_allowed_origins="*")

# Guarda os usuários conectados
usuarios = {}

@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("entrar")
def entrar(nome):
    usuarios[request.sid] = nome

    emit("mensagem", {
        "autor": "Sistema",
        "texto": f"{nome} entrou no chat."
    }, broadcast=True)

    emit("usuarios", list(usuarios.values()), broadcast=True)


@socketio.on("mensagem")
def mensagem(data):
    emit("mensagem", data, broadcast=True)


@socketio.on("disconnect")
def sair():
    nome = usuarios.pop(request.sid, None)

    if nome:
        emit("mensagem", {
            "autor": "Sistema",
            "texto": f"{nome} saiu do chat."
        }, broadcast=True)

        emit("usuarios", list(usuarios.values()), broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
