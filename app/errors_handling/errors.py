from fastapi.responses import JSONResponse
from typing import Optional, Any

A2A_ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603,
    "SERVER_ERROR": -32000,  # you can customize sub-ranges like -32001, -32002...
}

def a2a_error_response(
    request_id: Optional[str],
    code: int,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 400,
):
    """Return JSON-RPC-style A2A error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
                "data": {"details": details} if details else None
            }
        },
    )