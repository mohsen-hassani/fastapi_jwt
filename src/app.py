from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.auth.jwt_handler import JWThandler
from src.auth.payload_model import RoleType
from src.exceptions import UsernameAlreadyExistsError,UserNotFound
from src.usecases.get_current_user import GetCurrentLoggedInUser
from src.usecases.login import Login
from src.usecases.logout import Logout
from src.usecases.register_user import RegisterUser
from src.usecases.reset_password import ResetPassword


app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = JWThandler.read_token(token)
    return {"username": payload["sub"]}


@app.get("/admin")
def admin_route():
    return {"this path is available only for admins"}


@app.post("/register")
def register_user(username, password, name, email, role: RoleType):
    user_data = {
        "username": str(username),
        "password": str(password),
        "name": str(name),
        "email": str(email),
        "role": str(
            role.value.lower()
        ),  # Convert the RoleType enum to its string representation
    }

    register_user = RegisterUser()

    try:
        register_user.execute(user_data)
        return {"message": "User register successfully", "user_inofo": user_data}
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    login_user = Login()

    username = form_data.username
    password = form_data.password

    result = login_user.execute(username, password)
    return result


@app.post("/verify")
def verify():
    pass


@app.post("/refresh")
def refresh():
    pass


@app.get("/logout")
def logout(user:str):

    logout_use_case = Logout()
    logout_successful, message = logout_use_case.execute(user)
    
    if logout_successful:
        return {"message": message}
    else:
        return {"message": message}

@app.get("/me")
def get_current_user(token : str):
    current_user_usecase = GetCurrentLoggedInUser()
    user_info = current_user_usecase.execute(token)
    return user_info



@app.post("/reset-password")
def reset_password(userame:str,current_password:str, new_password:str):
    rest_user_password = ResetPassword()
    reset_successful,message =rest_user_password.execute(userame,current_password,new_password)

    if reset_successful:
        return {"message": message}
    else:
        return {"message": message}

