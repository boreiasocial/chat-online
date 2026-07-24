from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat-online"

socketio = SocketIO(app, cors_allowed_origins="*")

usuarios = set()

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("entrar")
def entrar(nome):
    usuarios.add(nome)
    emit("mensagem", {
        "autor": "Sistema",
        "texto": f"{nome} entrou no chat!"
    }, broadcast=True)

    emit("usuarios", list(usuarios), broadcast=True)

@socketio.on("mensagem")
def mensagem(data):
    emit("mensagem", data, broadcast=True)

@socketio.on("disconnect")
def sair():
    # Nesta primeira versão não removemos o usuário pelo nome,
    # isso vamos melhorar depois.
    emit("mensagem", {
        "autor": "Sistema",
        "texto": "Um usuário saiu."
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
