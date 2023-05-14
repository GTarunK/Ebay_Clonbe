from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import relationship, Session

app = FastAPI()
templates = Jinja2Templates(directory = "templates")

models.Base.metadata.create_all(bind=engine)

def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()


@app.get('/')
def welcome(request:Request):
	return templates.TemplateResponse("front_page.html",{"request":request})

@app.get('/login')
def welcome(request:Request):
	return templates.TemplateResponse("login.html",{"request":request})

@app.get('/signup')
def welcome(request:Request):
	return templates.TemplateResponse("signup.html",{"request":request})


@app.post('/register_user')
def save_user_data(request:Request, name:str = Form(...), email:str = Form(...), password:str = Form(...), db:Session = Depends(get_db)):
	user = models.Users()
	user.name = name
	user.email = email
	user.password = password
	userExists = db.query(models.Users).filter(models.Users.email == email).first()
	if userExists:
		return {"message":"User already exists"}
	else:
		db.add(user)
		db.commit()
	return {"message":"Registration Successful"}

@app.post('/login_user')
def login_user(request:Request, email:str = Form(...), password:str = Form(...), db:Session = Depends(get_db)):
	userExists = db.query(models.Users).filter(models.Users.email == email).first()
	if userExists:
		userExists = db.query(models.Users).filter(models.Users.email == email, models.Users.password == password).first()
		if userExists:
			return {"User Login Successful"}
		else:
			return {"Incorrect Password"}
	else:
		return {"user doesn't exist"}
