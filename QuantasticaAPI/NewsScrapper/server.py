from flask import Flask, request, jsonify
from contentFetcher import getContent,getHeadline
from flask_cors import CORS
app = Flask(__name__)
CORS(app, origins=["*"])  # Enable CORS for all origins
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the News Content Fetcher API!",
        "endpoints": {
            "/getNews": "Fetch full news articles by topic (GET request with JSON body containing 'topic')",
            "/getHeadlines": "Fetch news headlines by topic (GET request with JSON body containing 'topic')"
        },
        "status": "online"
    })
@app.route('/getNews', methods=['POST'])
def content():
    req_data = request.get_json()
    if not req_data or 'topic' not in req_data:
        return jsonify({"error": "Missing topic parameter"}), 400
    topic = req_data['topic']
    data = getContent(topic)
    return jsonify(data)

@app.route('/getHeadlines', methods=['POST'])
def headlines():
    req_data = request.get_json()
    if not req_data or 'topic' not in req_data:
        return jsonify({"error": "Missing topic parameter"}), 400
    topic = req_data['topic']
    data = getHeadline(topic)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
