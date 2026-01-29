from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Webhook server running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Extract required fields
    author = data["pusher"]["name"]
    to_branch = data["ref"].split("/")[-1]
    timestamp = data["head_commit"]["timestamp"]

    # Print required format
    print(f'{author} pushed to {to_branch} on {timestamp}')

    return "", 200

if __name__ == "__main__":
    app.run(port=5000)
