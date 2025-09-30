from flask import Flask, jsonify, request

dictionary_api = Flask(__name__)

dictionary = {
    "hello": {"definition": "Used to greet someone", "partOfSpeech": "exclamation"},
    "world": {"definition": "The earth and everything on it", "partOfSpeech": "noun"}
}



@dictionary_api.route("/api/entries/<word>", methods=["GET"])
def get_word(word):
    word = word.lower()
    if word in dictionary:
        return jsonify({"word": word, "data": dictionary[word]})
    else:
        return jsonify({"error": "Word not found"}), 404

# Cache
@dictionary_api.route("/api/entries-cache/<word>", methods=["GET"])
def get_word_in_cache(word):
    word = word.lower()
    response = jsonify({"word": word, "data": dictionary.get(word, {"definition": "Not found"})})
    response.headers["Cache-Control"] = "max-age=60"  # Lưu cache 60 giây
    return response


@dictionary_api.route("/api/code-on-demand", methods=["GET"])
def code_on_demand():
    response = jsonify({
        "script": "print('Đoạn code trong script')"
    })
    return response

@dictionary_api.route("/api/entries-hateoas/<word>", methods=["GET"])
def get_word_with_hateoas(word):
    word = word.lower()
    data = dictionary.get(word, {"definition": "Not found"})
    links = {
        "self": f"/api/entries-hateoas/{word}",
        "related": "/api/entries/hello"
    }
    return jsonify({"word": word, "data": data, "links": links})



@dictionary_api.before_request
def proxy_layer():
    print("Middle Layer", request.path)

@dictionary_api.route("/api/entries-layered/<word>", methods=["GET"])
def get_word_layered(word):
    word = word.lower()
    data = dictionary.get(word, {"definition": "Not found"})
    return jsonify({"word": word, "data": data, "Middle Layer": True})

if __name__ == "__main__":
    dictionary_api.run(debug=True)
