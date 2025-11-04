from uuid import uuid4

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

from app.errors_handling.errors import a2a_error_response, A2A_ERROR_CODES
from app.schemas import JSONRPCRequest, A2AMessage, JSONRPCResponse, TaskResult, TaskStatus, Artifact, MessagePartText
from app.service.fetch_anagrams import  fetch_anagrams

router = APIRouter()


# @router.post("/a2a/anagram")
# async def handle_a2a(request: JSONRPCRequest):
#     print("Received A2A anagram request\n")
#
#     request_id = getattr(request, "id", None)
#
#     try:
#         # --- Extract message safely ---
#         user_message = request.params.message if request.params else None
#         if not user_message:
#             return a2a_error_response(
#                 request_id,
#                 A2A_ERROR_CODES["INVALID_REQUEST"],
#                 "Missing or malformed 'params.message'"
#             )
#
#         print(f"@@@ Incoming messageId: {user_message.messageId}")
#
#         # --- Extract word ---
#         word = None
#         for part in user_message.parts or []:
#             if part.kind == "text" and getattr(part, "text", None):
#                 word = part.text.strip()
#                 break
#             elif part.kind == "data" and hasattr(part, "data"):
#                 for inner in part.data:
#                     if getattr(inner, "text", None):
#                         word = inner.text.strip()
#                         break
#                 if word:
#                     break
#
#         if not word:
#             return a2a_error_response(
#                 request_id,
#                 A2A_ERROR_CODES["INVALID_PARAMS"],
#                 "No valid text found in message parts",
#                 "Ensure your message.parts include a text field"
#             )
#
#         print(f"@@@ Word received: {word}")
#
#         # --- Process ---
#         anagrams = fetch_anagrams(word)
#         print(f"@@@ Anagrams: {anagrams}")
#
#         # --- Build result ---
#         agent_message = A2AMessage(
#             role="agent",
#             parts=[MessagePartText(kind="text", text=anagrams)]
#         )
#
#         artifacts = []
#         if anagrams:
#             artifacts.append(
#                 Artifact(
#                     name="anagrams",
#                     parts=[MessagePartText(kind="text", text=anagrams)]
#                 )
#             )
#
#         result = TaskResult(
#             id=str(uuid4()),
#             contextId=str(uuid4()),
#             status=TaskStatus(state="completed", message=agent_message),
#             artifacts=artifacts,
#             history=[user_message, agent_message],
#         )
#
#         return JSONRPCResponse(id=request.id, result=result).model_dump()
#
#     except ValueError as e:
#         # e.g., malformed data, bad parameter
#         return a2a_error_response(
#             request_id,
#             A2A_ERROR_CODES["INVALID_PARAMS"],
#             "Invalid params",
#             str(e),
#             status_code=400,
#         )
#
#     except Exception as e:
#         # fallback — internal or unexpected errors
#         return a2a_error_response(
#             request_id,
#             A2A_ERROR_CODES["INTERNAL_ERROR"],
#             "Internal error",
#             str(e),
#             status_code=500,
#         )

@router.post("/a2a/anagram")
async def handle_a2a(request: Request):
    print("Received A2A anagram request\n")

    # --- Step 1: Parse raw JSON safely ---
    try:
        payload = await request.json()
    except Exception as e:
        # Parse error (-32700)
        return a2a_error_response(
            None,
            A2A_ERROR_CODES["PARSE_ERROR"],
            "Parse error",
            f"Invalid JSON: {str(e)}",
            status_code=400,
        )

    # --- Step 2: Basic JSON-RPC validation ---
    request_id = payload.get("id")
    jsonrpc = payload.get("jsonrpc")
    method = payload.get("method")
    params = payload.get("params")

    if jsonrpc != "2.0" or not isinstance(params, dict):
        return a2a_error_response(
            request_id,
            A2A_ERROR_CODES["INVALID_REQUEST"],
            "Invalid Request",
            "Missing or malformed 'jsonrpc' or 'params' field",
            status_code=400,
        )

    # --- Step 3: Extract message ---
    user_message = params.get("message")
    if not user_message:
        return a2a_error_response(
            request_id,
            A2A_ERROR_CODES["INVALID_REQUEST"],
            "Missing or malformed 'params.message'",
            status_code=400,
        )

    print(f"@@@ Incoming messageId: {user_message.get('messageId')}")

    # --- Step 4: Extract word ---
    word = None
    parts = user_message.get("parts", [])
    for part in parts:
        kind = part.get("kind")
        if kind == "text" and part.get("text"):
            word = part["text"].strip()
            break
        elif kind == "data" and "data" in part:
            for inner in part["data"]:
                if inner.get("text"):
                    word = inner["text"].strip()
                    break
            if word:
                break

    if not word:
        return a2a_error_response(
            request_id,
            A2A_ERROR_CODES["INVALID_PARAMS"],
            "No valid text found in message parts",
            "Ensure your message.parts include a text field",
            status_code=400,
        )

    print(f"@@@ Word received: {word}")

    # --- Step 5: Process ---
    try:
        anagrams = fetch_anagrams(word)
        print(f"@@@ Anagrams: {anagrams}")
    except Exception as e:
        return a2a_error_response(
            request_id,
            A2A_ERROR_CODES["SERVER_ERROR"],
            "Server error",
            f"Failed to fetch anagrams: {str(e)}",
            status_code=502,
        )

    # --- Step 6: Build response ---
    agent_message = {
        "role": "agent",
        "parts": [{"kind": "text", "text": anagrams}]
    }

    artifacts = []
    if anagrams:
        artifacts.append({
            "name": "anagrams",
            "parts": [{"kind": "text", "text": anagrams}]
        })

    result = {
        "id": str(uuid4()),
        "contextId": str(uuid4()),
        "status": {"state": "completed", "message": agent_message},
        "artifacts": artifacts,
        "history": [user_message, agent_message],
    }

    # --- Step 7: Return success response ---
    return JSONResponse(
        status_code=200,
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        },
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



