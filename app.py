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
    """Receives GitHub webhook events (Push event).
    Extracts required fields and stores them in MongoDB."""
    data = request.json

    # Extract required fields from webhook payload
    document = {
        "request_id": data["after"],                  # Commit SHA
        "author": data["pusher"]["name"],             # GitHub username
        "action": "PUSH",                              # Event type
        "from_branch": None,                           # Not applicable for push
        "to_branch": data["ref"].split("/")[-1],       # Branch name
        "timestamp": data["head_commit"]["timestamp"]  # Event time
    }

    # Insert event into MongoDB
    collection.insert_one(document)

    # Log output in required format
    print(f'{document["author"]} pushed to {document["to_branch"]} on {document["timestamp"]}')

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
