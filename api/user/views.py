from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.exceptions import DoesNotExist

from models.app_models import User_Pydantic, User, UserDTO, UserIn_Pydantic, UserUpdateDTO
import jwt

auth = APIRouter()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
JWT_SECRET = 'myjwtsecret'


async def auth_user(username: str, password: str):
    try:
        user = await User.get(username=username)
        if not user:
            return False
        if not user.verify_password(password):
            return False
        return user
    except DoesNotExist:
        return False


@auth.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
    return await User_Pydantic.from_tortoise_orm(user)


@auth.get('/users')
async def get_users():
    try:
        users = await User.all()
        return users
    except HTTPException as e:
        return {'error': str(e)}


@auth.put('/users/{user_id}', response_model=User_Pydantic)
async def update_user(user_id: int, user_data: UserUpdateDTO):
    try:
        # Retrieve the existing user
        user = await User.get(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user fields from the data provided
        user.username = user_data.username if user_data.username else user.username
        user.email = user_data.email if user_data.email else user.email
        user.name = user_data.name if user_data.name else user.name
        user.surname = user_data.surname if user_data.surname else user.surname
        user.thirdname = user_data.thirdname if user_data.thirdname else user.thirdname
        user.is_admin = user_data.is_admin if user_data.is_admin is not None else user.is_admin

        # Save the changes
        await user.save()

        # Return the updated user data
        return await User_Pydantic.from_tortoise_orm(user)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth.delete('/users/{user_id}')
async def delete_user(user_id: int):
    try:
        user = await User.get(id=user_id)
        if user:
            await user.delete()
            return {"detail": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
    except HTTPException as e:
        return {'error': str(e)}


@auth.post('/users', response_model=User_Pydantic)
async def create_user(user: UserDTO):
    user_obj = await User(
        username=user.username,
        password_hash=bcrypt.hash(user.password),
        email=user.email,
        name=user.name,
        surname=user.surname,
        thirdname=user.thirdname,
        is_admin=user.is_admin
    )
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)


@auth.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user
