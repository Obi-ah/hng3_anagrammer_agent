import json
import os
from contextlib import contextmanager, asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.router import router


app = FastAPI(title='Anagram Agent')
app.include_router(router)


@app.middleware("http")
async def log_request_response(request: Request, call_next):
    print("\n\n➡️", request.method, request.url)

    # Try to read request body
    try:
        body = await request.json()
        print(f"📦 Request Body: {body}")
    except Exception:
        print("📭 No JSON body or unreadable body")

    # Get raw response
    response = await call_next(request)

    # Clone and log response body
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    try:
        decoded = json.loads(response_body.decode("utf-8"))
        print(f"📤 Response: {json.dumps(decoded, indent=2)}")
    except Exception:
        print(f"📤 Response Body (raw): {response_body.decode('utf-8', 'ignore')[:300]}")

    # Return a new Response so FastAPI can send it back to the client
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

#
# from app.exceptions.handlers import register_exception_handlers
# register_exception_handlers(app)


@app.get('/')
def read_root():
    return {"message": "Welcome!"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))