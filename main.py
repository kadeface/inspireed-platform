from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/languages", methods=["GET"])
def get_languages():
    languages = [
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "JavaScript"},
        {"id": 3, "name": "Java"},
        {"id": 4, "name": "C#"},
        {"id": 5, "name": "C++"},
    ]
    return jsonify(languages)


if __name__ == "__main__":
    app.run(debug=True)

