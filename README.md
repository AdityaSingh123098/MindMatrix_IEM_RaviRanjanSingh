# 🛰️ Communication Gap Detector

> **AI-Free, Deterministic NLP System for Detecting and Pinpointing Communication Breakdowns in Multi-Participant Team Conversations.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://palletsprojects.com/p/flask/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Engine-Rule--Based%20NLP-orange.svg)](#detection-rules)

---

## 📌 Problem Statement

In fast-paced, asynchronous, and hybrid team environments, critical communication failures occur daily:
* **Questions go unanswered** as threads drift or move too quickly.
* **Requests are ignored or repeated multiple times** due to unfulfilled promises or vague acknowledgments.
* **Vague instructions spark clarification loops**, leaving team members confused and blocked.
* **Crucial topics and action items are abandoned** without decisions or ownership.

Traditional LLM-based solutions suffer from **high operational cost**, **data privacy concerns**, **nondeterministic hallucinated outputs**, and **latency bottlenecks**. Teams need a lightweight, explainable, and instantaneous system that diagnoses exactly *where* and *why* communication failed.

---

## 💡 Solution Overview

**Communication Gap Detector** is a full-stack, hackathon-ready web application built using Python, Flask, and standard web technologies. It parses multi-participant chat transcripts into chronological conversational turns and runs a deterministic, rule-based NLP pipeline to identify four primary communication gaps:

1. **Unanswered Questions**
2. **Repeated Requests**
3. **Repeated Clarification Requests**
4. **Unresolved Topics**

Each detected gap includes the **speaker**, the **exact message**, and **transparent evidence** showing where the breakdown happened.

---

## 🏛️ Architecture Diagram

```
+-------------------------------------------------------------+
|                     Frontend (Web UI)                       |
|   HTML5 / CSS3 / ES6 JavaScript                             |
|   - Multi-Scenario Presets Loader                           |
|   - Real-time Line Counter & Keyboard Shortcut              |
|   - Interactive Results Cards & Health Score Gauge          |
|   - Synchronized Transcript View with Gap Highlighting      |
+------------------------------+------------------------------+
                               |
                   HTTP POST   |   JSON Response
                   /analyze    |   (Gaps, Metrics, Messages)
                               v
+-------------------------------------------------------------+
|                     Flask Backend (app.py)                  |
|   - Route Handlers (/, /analyze, /api/samples)              |
|   - Input Validation & Normalization                        |
|   - Error Handling & JSON Serialization                     |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|             Analyzer Engine (analyzer.py)                   |
|   +-----------------------------------------------------+   |
|   | 1. Transcript Parser (Regex multi-format extractor) |   |
|   +-----------------------------------------------------+   |
|   | 2. Feature Extractor (Interrogatives, Imperatives)  |   |
|   +-----------------------------------------------------+   |
|   | 3. Gap Detection Modules:                           |   |
|   |    - Rule A: Unanswered Question Detector           |   |
|   |    - Rule B: Repeated Request Detector              |   |
|   |    - Rule C: Repeated Clarification Detector        |   |
|   |    - Rule D: Unresolved Topic Detector              |   |
|   +-----------------------------------------------------+   |
|   | 4. Health Scorer & Deduplication Engine             |   |
|   +-----------------------------------------------------+   |
+-------------------------------------------------------------+
```

---

## 🔍 Detection Rules

| Gap Type | Trigger Criteria | Resolution Criteria | Evidence Provided |
| :--- | :--- | :--- | :--- |
| **Unanswered Question** | Message ends with `?` or begins with interrogatives (`who`, `what`, `when`, etc.). | Subsequent response from another participant providing temporal, locational, or topical alignment. | Pinpoints following messages that shifted topics without answering. |
| **Repeated Request** | Action requests matching patterns like `can you send`, `please provide`, `kindly share`. | Intervening confirmation of delivery (`sent`, `attached`, etc.). | Links first request ID and subsequent repeated request ID. |
| **Repeated Clarification** | Phrases like `what do you mean?`, `which one?`, `can you clarify?`, `i don't understand`. | Elaboration resolving confusion. | Counts cumulative clarification requests demonstrating persistent ambiguity. |
| **Unresolved Topic** | Topics introduced via `about X`, `regarding X`, `update on X`, `issue with X`. | Concluding agreement or action keyword (`done`, `fixed`, `approved`, `decided`, etc.). | Explains that the topic was raised but no consensus or next step was established. |

---

## 🛠️ Technology Stack

* **Backend:** Python 3.9+, Flask 3.x
* **NLP & Parsing:** Python Regular Expressions (`re`), Collections, Deterministic Rule Heuristics
* **Frontend:** Semantic HTML5, Custom CSS3 (Modern Glassmorphism & Responsive Grid), Vanilla ES6+ JavaScript
* **Testing:** Python `unittest` framework

> **Strict AI-Free Constraint:** No external LLM APIs (OpenAI, Anthropic, Gemini, etc.) are utilized. The engine is 100% deterministic, explainable, lightweight, and runs entirely on your local machine.

---

## 📂 Project Structure

```
communication-gap-detector/
│
├── app.py                      # Flask backend entry point & REST API routes
├── analyzer.py                 # Core rule-based communication gap analyzer
├── test_analyzer.py            # Unit test suite verifying all detection rules
├── verify_samples.py           # Verification script for sample conversations
├── requirements.txt            # Python dependencies
├── README.md                   # Complete project documentation
│
├── data/
│   └── sample_conversations.json # 6 pre-loaded test scenarios for testing
│
├── docs/
│   └── gap_definitions.md     # Deep dive into definitions, rules & impact
│
├── templates/
│   └── index.html              # Responsive web application interface
│
└── static/
    ├── style.css               # Clean modern developer-grade UI styles
    └── script.js               # Interactive frontend controller & sync logic
```

---

## 🚀 How to Run

### 1. Prerequisites
* Python 3.9 or higher installed on your system.

### 2. Clone or Navigate to the Directory
```bash
cd communication-gap-detector
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Tests
```bash
python test_analyzer.py
```

### 5. Launch the Web Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📥 Example Input

Paste this multi-person conversation into the analyzer:

```text
Neha: What time is the meeting?
Ravi: I am working on the report.
Soham: Can you send the dataset?
Ravi: Okay.
Soham: Can you send the dataset?
```

---

## 📤 Example Output

### JSON API Response (`POST /analyze`)
```json
{
  "gaps": [
    {
      "type": "Unanswered Question",
      "speaker": "Neha",
      "message": "What time is the meeting?",
      "evidence": "Question received no direct response. Subsequent responses shifted topics without addressing it (e.g., Ravi: 'I am working on the report.'; Soham: 'Can you send the dataset.')."
    },
    {
      "type": "Repeated Request",
      "speaker": "Soham",
      "message": "Can you send the dataset?",
      "evidence": "Request repeated without resolution. Originally requested in Message #3 by Soham, and repeated in Message #5 by Soham due to lack of fulfillment."
    }
  ]
}
```

### UI Features
* **Health Score:** Displays conversation health (0–100) based on gap density.
* **Participant Badges:** Automatically identifies unique conversational participants.
* **Interactive Transcript:** Highlights flagged messages with colored badges; clicking any diagnostic card smoothly jumps to the message in context.
* **Filter Chips:** Filter results by Questions, Requests, Clarifications, or Topics.
* **One-Click JSON Export:** Easily copy the raw JSON output to clipboard for reporting.

---

## 🔮 Future Enhancements

1. **Slack & Discord Bot Integrations:** Real-time channel bots that gently nudge teams when questions go unanswered for >3 hours.
2. **Audio Meeting Transcripts:** Direct ingestion of Whisper/Zoom/Teams automated transcripts with speech-to-text timing metadata.
3. **Sentiment & Urgency Scoring:** Prioritizing critical production blockers over casual banter.
4. **Auto-Remediation Suggestions:** Automated drafting of follow-up reminder messages to help teams close communication gaps faster.

---

## 📄 License

This project is licensed under the MIT License.
