from uuid import uuid4

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

from app.schemas import JSONRPCRequest, A2AMessage, JSONRPCResponse, TaskResult, TaskStatus, Artifact, MessagePartText
from app.service.fetch_anagrams import  fetch_anagrams

router = APIRouter()


@router.post("/a2a/anagram")
async def handle_a2a(request: JSONRPCRequest):
    print("Received A2A anagram request\n")

    try:
        # --- Extract message ---
        user_message = request.params.message
        print(f"@@@ Incoming messageId: {user_message.messageId}")

        # --- Extract word from message parts ---
        word = None
        for part in user_message.parts:
            # direct text part
            if hasattr(part, "text") and part.kind == "text" and part.text:
                word = part.text.strip()
                break
            # nested data list
            elif hasattr(part, "data") and part.kind == "data":
                for inner in part.data:
                    if inner.text and inner.text.strip():
                        word = inner.text.strip()
                        break
                if word:
                    break

        if not word:
            raise ValueError("No valid text found in message parts")

        print(f"@@@ Word received: {word}")

        # --- Process anagrams ---
        anagrams = fetch_anagrams(word)
        print(f"@@@ Anagrams: {anagrams}")

        # --- Build agent message ---
        response_text = anagrams
        agent_message = A2AMessage(
            role="agent",
            parts=[MessagePartText(kind="text", text=response_text)]
        )

        # --- Build artifacts ---
        artifacts = []
        if anagrams:
            artifacts.append(
                Artifact(
                    name="anagrams",
                    parts=[MessagePartText(kind="text", text=anagrams)]
                )
            )

        # --- Construct result ---
        result = TaskResult(
            id=str(uuid4()),
            contextId=str(uuid4()),
            status=TaskStatus(state="completed", message=agent_message),
            artifacts=artifacts,
            history=[user_message, agent_message],
        )

        print(f"@@@ Returning {len(anagrams)} anagrams as artifact\n")

        # --- Return successful JSON-RPC response ---
        return JSONRPCResponse(id=request.id, result=result).model_dump()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"details": str(e)}
                }
            }
        )


@router.get("/.well-known/agent.json")
def get_agent_card():
    return JSONResponse(
        content={
            "name": "AnagramAgent",
            "description": "An agent that returns all possible anagrams of a provided word.",
            "url": f"https://hng3-anagrammer.fly.dev/a2a/anagram",
            "version": "1.0.0",

            "documentationUrl": f"https://hng3-anagrammer.fly.dev/docs",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False
            },
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["application/json", "text/plain"],
            "skills": [
                {
                    "id": "anagram-skill-001",
                    "name": "Find Anagrams",
                    "description": "Generates all valid anagrams of a given word.",
                    "inputModes": ["text/plain"],
                    "outputModes": ["text/plain"],
                    "examples": [
                        {
                            "input": {
                                "parts": [{"text": "eat", "contentType": "text/plain"}]
                            },
                            "output": {
                                "parts": [{"text": "tea, ate", "contentType": "text/plain"}]
                            }
                        }
                    ]
                }
            ],
            "supportsAuthenticatedExtendedCard": False
        }
    )


@router.get("/health")
def health_check():
    print("@@@ health")
    return {"status": "ok", "agent": "anagram"}



