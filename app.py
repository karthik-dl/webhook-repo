from flask import Flask, request, render_template
from pymongo import MongoClient

# Flask App Initialization
app = Flask(__name__)


# MongoDB Configuration
# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")
db = client["github_events"]
collection = db["events"]

# Home Route (Health Check)
@app.route("/")
def home():
    #Simple health check route to confirm server is running
    return "Webhook server running"


# GitHub Webhook Endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles GitHub webhook events:
    - PUSH
    - MERGE (via Pull Request merged)
    """
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")


    # PUSH EVENT
    if event_type == "push":
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


    # MERGE EVENT (Pull Request merged)
    elif event_type == "pull_request" and data.get("pull_request", {}).get("merged"):
        pr = data["pull_request"]

        document = {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "MERGE",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": pr["merged_at"]
        }

        collection.insert_one(document)

        print(
            f'{document["author"]} merged branch '
            f'{document["from_branch"]} to {document["to_branch"]} '
            f'on {document["timestamp"]}'
        )

    return "", 200


# API to Fetch Latest Events
@app.route("/events", methods=["GET"])
def get_events():
    """Fetches latest GitHub events from MongoDB
    Used by UI to poll data every 15 seconds"""
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


# UI Route
@app.route("/ui")
def ui():
    """
    Renders the UI page that displays GitHub events
    """
    return render_template("index.html")


# Application Entry Point
if __name__ == "__main__":
    app.run(port=5000)
