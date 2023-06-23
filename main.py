from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import relationship, Session
from fastapi.responses import HTMLResponse

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
	cookie = request.cookies.get("user_name")
	if cookie is None:
		return templates.TemplateResponse("front_page.html",{"request":request})
	else:
		return templates.TemplateResponse("home.html",{"request":request,"user_details":cookie})

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

@app.post('/login_user',)
async def login_user(request:Request, email:str=Form(...), password:str=Form(...), db:Session=Depends(get_db)):
	userExists = models.Users()
	userExists = db.query(models.Users).filter(models.Users.email == email).first() 
	if userExists:
		userExists = db.query(models.Users).filter(models.Users.email == email, models.Users.password == password).first()
		if userExists:
			response = templates.TemplateResponse("home.html",{"request":request,"user_details":userExists.name})
			response.set_cookie(key="user_id",value=userExists.id,path="/")
			response.set_cookie(key="user_name",value=userExists.name,path="/")
			return response 
		else:
			return {"Please check your password"}
	else:
		return {"message":"User does not exists"}

@app.get('/logout')
def welcome(request:Request):
	response = templates.TemplateResponse("front_page.html",{"request":request})
	response.delete_cookie(key="user_id",path="/")
	response.delete_cookie(key="user_name",path="/")
	return response 

@app.get('/create_listings')
def welcome(request:Request):
	return templates.TemplateResponse("create_listings.html",{"request":request})


@app.post('/create_listing/{user_id}')
async def create_listing_data(user_id:int,request:Request,title:str=Form(...),price:float=Form(...),description:str=Form(...),image:str=Form(...),categories:str=Form(...), db:Session=Depends(get_db)):
	listing = models.Listings()
	listing.user_id = user_id
	listing.product_title = title 
	listing.price = price
	listing.description = description 
	listing.image = image 
	listing.category = categories 
	print(categories)
	db.add(listing)
	db.commit()
	listings_data = db.query(models.Listings).all()
	return templates.TemplateResponse("active_listings.html",{"request":request,"listings_data":listings_data})

@app.get('/active_listings')
def welcome(request:Request, db:Session=Depends(get_db)):
	listings_data = db.query(models.Listings).all()
	return templates.TemplateResponse("active_listings.html",{"request":request, "listings_data":listings_data})

@app.get('/categories')
def welcome(request:Request,db:Session=Depends(get_db)):
	listings_data = db.query(models.Listings).all()
	print(listings_data)
	result = [row.__dict__ for row in listings_data]
	categories = {}
	for product in result:
		category = product["category"]
		if category not in categories:
			categories[category] = []
		categories[category].append(product)
	print(categories)
	return templates.TemplateResponse("categories.html",{"request":request,"categories":categories})
