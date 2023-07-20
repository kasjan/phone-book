import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from database import Base, get_db
from main import app

DATABASE_USERNAME = config.DATABASE_USERNAME
DATABASE_PASSWORD = config.DATABASE_PASSWORD
DATABASE_HOST = config.DATABASE_HOST
DATABASE_NAME = config.DATABASE_NAME

DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user():
    return {"username": "john@gmail.com", "password": "pass"}


def test_create_user():
    response = client.post('/user/create',
                           json={'nickname': 'John', 'email': 'john@gmail.com', 'password': 'pass'}, )
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'john@gmail.com'
    assert data['nickname'] == 'John'


def test_create_user_validation():
    response = client.post('/user/create',
                           json={'nickname': 'John', 'email': 'invalidemail', 'password': 'pass'}, )
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'value is not a valid email address: The email address is not ' \
                                                  'valid. It must have exactly one @-sign.'


def test_get_user():
    response = client.get('/user/1')
    assert response.status_code == 200


def test_login():
    response = client.post('/user/login', data={'username': 'john@gmail.com', 'password': 'pass'})
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    return token


def test_login_wrong_password():
    response = client.post('/user/login', data={'username': 'john@gmail.com', 'password': 'wrong'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'


def test_login_wrong_email():
    response = client.post('/user/login', data={'username': 'joxxhn@gmail.com', 'password': 'pass'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'


def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'msg': 'Phone Book API homepage'}


def test_unauthorized_show_all_contacts():
    response = client.get("/contacts/all")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_unauthorized_add_contact():
    response = client.get("/contacts")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_unauthorized_delete_contact():
    response = client.delete("/contacts/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_unauthorized_update_contact():
    response = client.put("/contacts/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_unauthorized_get_contact():
    response = client.get("/contacts/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_all_contacts():
    token = test_login()
    response = client.get("/contacts/all", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_create_contact():
    token = test_login()
    response = client.post("/contacts",
                           json={'first_name': 'John', 'last_name': 'Smith',
                                 'phone_number': '911', 'email': 'user@email.com'},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data['first_name'] == 'John'
    assert data['last_name'] == 'Smith'
    assert data['phone_number'] == '911'
    assert data['email'] == 'user@email.com'


def test_create_contact_wrong_phone_number():
    token = test_login()
    response = client.post("/contacts", json={'first_name': 'John', 'last_name': 'Smith', 'phone_number': 'wrongnumber',
                                              'email': 'user@email.com'}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid phone number format'


def test_create_contact_wrong_email():
    token = test_login()
    response = client.post("/contacts", json={'first_name': 'John', 'last_name': 'Smith', 'phone_number': '911',
                                              'email': 'useremail'}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'value is not a valid email address: The email address is not ' \
                                                  'valid. It must have exactly one @-sign.'


def test_get_contact_by_id():
    token = test_login()
    response = client.get('/contacts/1', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_get_logged_in_user_contacts():
    token = test_login()
    response = client.get('/contacts', headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert response.status_code == 200
    assert data[0]['first_name'] == 'John'
    assert data[0]['last_name'] == 'Smith'
    assert data[0]['phone_number'] == '911'
    assert data[0]['email'] == 'user@email.com'


def test_update_contact():
    token = test_login()
    response = client.put('/contacts/1',
                          json={'first_name': 'Stan', 'last_name': 'Lee',
                                'phone_number': '119', 'email': 'custom@mail.com'},
                          headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert response.status_code == 202
    assert data == 'Contact 1 updated!'


def test_delete_contact():
    token = test_login()
    response = client.delete('/contacts/1', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_delete_contact_invalid():
    token = test_login()
    response = client.delete('/contacts/999', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()['detail'] == 'Contact with id 999 not found.'
