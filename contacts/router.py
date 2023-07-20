from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from account import schemas as user_schemas
from account.jwt import get_current_user
from contacts import models, schemas
from database import get_db

router = APIRouter(
    tags=['Contacts'],
    prefix='/contacts')


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.ShowContact])
async def get_logged_in_user_contacts(db: Session = Depends(get_db), current_user: user_schemas.User = Depends(get_current_user)):
    contacts = db.query(models.Contact).filter(models.Contact.user_id == current_user.user_id).all()
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Empty contact list')
    return contacts


@router.get('/all', status_code=status.HTTP_200_OK)
async def show_all_contacts(db: Session = Depends(get_db), current_user: user_schemas.User = Depends(get_current_user)):
    contacts = db.query(models.Contact).all()
    return contacts


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_contact(request: schemas.Contact, db: Session = Depends(get_db),
                         current_user: user_schemas.User = Depends(get_current_user)):
    new_test = models.Contact(
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
        email=request.email,
        user_id=current_user.user_id
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id, db: Session = Depends(get_db),
                         current_user: user_schemas.User = Depends(get_current_user)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id)
    if not contact.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with id {contact_id} not found.')
    contact.delete()
    db.commit()
    return f'Contact {id} deleted!'


@router.put('/{contact_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_contact(contact_id, request: schemas.Contact, db: Session = Depends(get_db),
                         current_user: user_schemas.User = Depends(get_current_user)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id)
    if not contact.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with id {contact_id} not found.')
    contact.update(request.model_dump(exclude_unset=True))
    db.commit()
    return f'Contact {contact_id} updated!'


@router.get('/{contact_id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowContact)
async def get_contact(contact_id, db: Session = Depends(get_db),
                      current_user: user_schemas.User = Depends(get_current_user)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with id {contact_id} not found.')
    return contact
