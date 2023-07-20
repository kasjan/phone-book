from fastapi import FastAPI

from account import router as account_router
from contacts import router as contacts_router

app = FastAPI()


@app.get("/", tags=['Root'])
async def root():
    return {"msg": "Phone Book API homepage"}


app.include_router(contacts_router.router)
app.include_router(account_router.router)
