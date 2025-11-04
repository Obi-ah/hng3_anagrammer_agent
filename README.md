# Anagram Agent

A lightweight **A2A-compliant FastAPI agent** that takes a word, sends it to the **Gemini LLM API**, and returns all possible anagrams.

---

## Overview

This agent follows the **Agent-to-Agent (A2A) protocol** for standardized communication between AI agents.  
It accepts `message/send` requests, processes the input word using **Gemini**, and returns structured responses containing generated anagrams.

---

## Features

-  A2A JSON-RPC support (`message/send`, `status`)
-  Gemini LLM integration for anagram generation
-  Modular FastAPI structure (`routers`, `services`, `models`)
-  A2A-style error responses
-  Request & response logging middleware
-  Deployable on Fly.io or Railway

---


---

## Setup

```bash
git clone https://github.com/obi-ah/hng3-anagrammer-agent.git
cd hng3-anagrammer-agent
python -m venv .venv
source .venv/bin/activate
pip install .
```

Create a `.env` file:
```
GEMINI_API_KEY
```

Run locally:
```bash
uvicorn app.main:app --reload
```

---

## 🧩 Example Request

```bash
curl -X POST http://localhost:8000/a2a   -H "Content-Type: application/json"   -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "angel"}]
      },
      "configuration": {
        "blocking": false,
        "acceptedOutputModes": ["text"],
        "historyLength": 1,
        "pushNotificationConfig": {}
      }
    }
  }'
```

### Sample Response
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "anagrams": ["angel", "glean", "genal", "lange"]
  }
}
```

