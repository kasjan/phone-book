from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from account import models, schemas
from account.hashing import Hash
from database import get_db

from .jwt import create_access_token

router = APIRouter(tags=['Accounts'],
                   prefix='/user'
                   )


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email is already used.')
    new_user = models.User(
        nickname=request.nickname,
        email=request.email,
        password=Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{user_id}', response_model=schemas.ShowUser)
async def get_user(user_id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id {user_id} not found.')
    return user


@router.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = create_access_token(data={"sub": user.email, 'user_id': user.id})
    return {"access_token": access_token, "token_type": "bearer"}
