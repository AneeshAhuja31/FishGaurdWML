from fastapi import Request,Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
import jwt
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your-default-secret-key")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    #dispact function runs for each request
    #request: upcoming http request
    #call_next fowards request to next middleware or endpoint
    async def dispatch(self, request:Request, call_next):
        request_id = str(time.time())
        start_time = time.time()

        logger.info(f"Request started: ID={request_id} {request.method} {request.url.path}")
        try:
            response = await call_next(request) #passes request to FastAPI to process it
            process_time = time.time() - start_time #measures time taken

            logger.info(f"Request completed: ID={request_id} Status={response.status_code} Time={process_time:.3f}s")
        
            response.headers["X-Process-Time"] = str(process_time) # Add processing time header to the response
            return response
        except Exception as e:
            logger.error(f"Request failed: ID={request_id} Error={str(e)}")
            raise

#Authentication middleware, used to verify a users's identity before allowing access to protected resources
class AuthMiddleware(BaseHTTPMiddleware): #checks if a request has a valid JWT token before allowing access to protected routes

    async def dispatch(self,request:Request,call_next):
        #skipauth for non protected routes
        if request.url.path in ['/','/docs','/openapi.json','/check-url','/check-job-posting']:
            return await call_next(request) 
        
        auth_header = request.headers.get('Authorization') #format: Authorization: Bearer <JWT_TOKEN>
        if not auth_header or not auth_header.startswith("Bearer "): 
            return Response(
                content=json.dumps({"detail": "Not authenticated"}),
                status_code=401,
                media_type="application/json"
            )
        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token,JWT_SECRET,algorithms=["HS256"])
            request.state.user_id = payload.get('sub')
        except jwt.PyJWTError:
            return Response(
                content=json.dumps({"detail": "Invalid token"}),
                status_code=401,
                media_type="application/json"
            )
        return await call_next(request)
    
def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add authentication middleware
    # Uncomment when deploying:
    # app.add_middleware(AuthMiddleware)