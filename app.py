from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Olá, Azure! 🚀"


if __name__ == "__main__":
    # Azure pode definir a porta por variável de ambiente
    import os
    port = int(os.environ.get("PORT", 8000))

    app.run(host="0.0.0.0", port=port)
