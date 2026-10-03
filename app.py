import os
import json
from flask import Flask, render_template, request, jsonify
from analyzer import CommunicationGapAnalyzer

app = Flask(__name__)
analyzer = CommunicationGapAnalyzer()

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SAMPLES_FILE = os.path.join(DATA_DIR, "sample_conversations.json")


def load_samples():
    if os.path.exists(SAMPLES_FILE):
        try:
            with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading sample conversations: {e}")
    return []


@app.route("/")
def index():
    samples = load_samples()
    return render_template("index.html", samples=samples)


@app.route("/analyze", methods=["POST"])
def analyze_conversation():
    conversation_text = ""

    if request.is_json:
        data = request.get_json(silent=True) or {}
        conversation_text = data.get("conversation", "")
    else:
        conversation_text = request.form.get("conversation", "")

    conversation_text = conversation_text.strip()

    if not conversation_text:
        return jsonify({
            "error": "Please provide a conversation transcript to analyze.",
            "gaps": [],
            "summary": {
                "total_messages": 0,
                "total_participants": 0,
                "participants": [],
                "total_gaps": 0,
                "health_score": 100,
                "gap_breakdown": {}
            },
            "messages": []
        }), 400

    try:
        results = analyzer.analyze(conversation_text)
        return jsonify(results), 200
    except Exception as e:
        app.logger.exception("Error analyzing conversation")
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "gaps": [],
            "summary": {},
            "messages": []
        }), 500


@app.route("/api/samples", methods=["GET"])
def get_samples():
    samples = load_samples()
    return jsonify({"samples": samples}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"\n>> Communication Gap Detector running at: http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
