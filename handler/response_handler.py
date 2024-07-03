from fastapi.responses import JSONResponse
from error_code import error

def handle_error(res,status_code=200):
    return JSONResponse({"code": res, "message": error.errorcode[res]}, status_code)