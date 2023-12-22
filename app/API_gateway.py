import json

from fastapi import FastAPI, Request, HTTPException, Depends
import httpx
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from json import JSONDecodeError

app = FastAPI()
discussion_board_url = "http://0.0.0.0:8000"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://0.0.0.0:8002/token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_requests(request: Request, path_name: str, token: str = Depends(oauth2_scheme)):
    # 剩余的路由逻辑...
    #token = request.headers.get("Authorization")
    token = token.split(" ")[-1] if token else None
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with httpx.AsyncClient() as client:
        if path_name.startswith("posts") or path_name.startswith("comments"):
            response = await client.request(
                method=request.method,
                url=f"{discussion_board_url}/{path_name}",
                headers=dict(request.headers),
                data=await request.body()
            )
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        else:
            raise HTTPException(status_code=404, detail="Service not found")

# @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def route_requests(request: Request, path_name: str):
#     token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#
#     user = await get_current_user(token)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     async with httpx.AsyncClient() as client:
#         if path_name.startswith("posts") or path_name.startswith("comments"):
#             response = await client.request(
#                 method=request.method,
#                 url=f"{discussion_board_url}/{path_name}",
#                 headers={key: value for key, value in request.headers.items()},
#                 data=await request.body()
#             )
#             return response.json()
#         else:
#             raise HTTPException(status_code=404, detail="Service not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)