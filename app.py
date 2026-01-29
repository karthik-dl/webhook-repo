from flask import Flask, request
from pymongo import MongoClient
from bson import ObjectId
from flask import render_template

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["github_events"]
collection = db["events"]


@app.route("/")
def home():
    return "Webhook server running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    document = {
        "request_id": data["after"],
        "author": data["pusher"]["name"],
        "action": "PUSH",
        "from_branch": None,
        "to_branch": data["ref"].split("/")[-1],
        "timestamp": data["head_commit"]["timestamp"]
    }

    collection.insert_one(document)

    print(f'{document["author"]} pushed to {document["to_branch"]} on {document["timestamp"]}')

    return "", 200

from bson import ObjectId

@app.route("/events", methods=["GET"])
def get_events():
    events = collection.find().sort("_id", -1).limit(10)

    result = []
    for event in events:
        result.append({
            "author": event["author"],
            "action": event["action"],
            "from_branch": event["from_branch"],
            "to_branch": event["to_branch"],
            "timestamp": event["timestamp"]
        })

    return {"events": result}

@app.route("/ui")
def ui():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000)
