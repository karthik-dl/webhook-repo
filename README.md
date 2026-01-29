# webhook-repo

A Flask-based GitHub webhook receiver application.

## Features
- Receives GitHub webhook events (Push)
- Extracts minimal required event data
- Stores events in MongoDB
- Exposes an API to fetch latest events
- Displays events on a UI that polls every 15 seconds

## Tech Stack
- Python (Flask)
- MongoDB
- HTML, JavaScript
- GitHub Webhooks

## Application Flow
1. A push event occurs in action-repo
2. GitHub sends the event to the Flask webhook endpoint
3. The webhook extracts required fields and stores them in MongoDB
4. The UI fetches data from the backend every 15 seconds and displays it

## Output Format
Example:
