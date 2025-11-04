import os
from contextlib import contextmanager, asynccontextmanager

from fastapi import FastAPI, Request
from app.router import router


app = FastAPI(title='Anagram Agent')
app.include_router(router)


@app.middleware("http")
async def log_request(request: Request, call_next):
    print('\n\n')
    print(f"➡️  {request.method} {request.url}")
    try:
        body = await request.json()
        print(f"📦 Body: {body}")
    except Exception:
        print("📭 No JSON body")

    print('\n\n')

    response = await call_next(request)
    return response

#
# from app.exceptions.handlers import register_exception_handlers
# register_exception_handlers(app)


@app.get('/')
def read_root():
    return {"message": "Welcome!"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))