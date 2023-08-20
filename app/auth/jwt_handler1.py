from datetime import datetime , timedelta
import uuid
from payload_model import JWTPayload
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
users_db = {
    "alice": {
        "hashed_password": "$2b$12$K.bAyVLZl6LXqlHHpS8A1eK.VX20TgI4AVnq3D0a0KSlOGy3TxHxe"
    }
}



class JWThandler:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def sign_jwt(username, name, email, role):
        jti = str(uuid.uuid4())
        expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        current_time = datetime.utcnow()
        epoch_time = int(current_time.timestamp())
        
        payload = JWTPayload(
            iss="jcommerce",
            sub=username,
            name=name,
            email=email,
            role=role,
            iat=epoch_time,
            exp=expiration,
            jti=jti,
            aud="https://your-app.com"
        )

        token = jwt.encode(payload.__dict__, SECRET_KEY, algorithm=ALGORITHM)
        return token










oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not JWThandler.verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = JWThandler.signJWT(username)
    return JWThandler.token_response(token)


@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = JWThandler.decodeJWT(token)
    return {"username": payload["sub"]}


# Explanation:

# JWThandler now has the verify_password method leveraging passlib to verify a hashed password.
# The users_db mock "database" contains a bcrypt hashed password for alice (which is "password").
# The /token route uses FastAPI's built-in OAuth2PasswordRequestForm to gather the username and password.
# The oauth2_scheme is an instance of OAuth2PasswordBearer, which provides a way to get the token from the request (typically the Authorization header).
# The protected_route function uses Depends(oauth2_scheme) to retrieve the token and then decodes it to verify.
# Note:

# This example demonstrates JWT-based authentication with password hashing but doesn't implement a full OAuth flow.
# In real-world applications, always keep secrets, keys, and passwords out of the code, preferably in environment variables.
# While this example uses an in-memory mock "database", in real applications, you'd fetch users and their hashed passwords from an actual database.
