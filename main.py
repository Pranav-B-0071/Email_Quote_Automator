import threading, json, httpx, os, time, uvicorn, psycopg2, schedule, asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from redis import Redis
from services.generate_quote import create_quotes
from services.send_email import send_mails
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from database import models
from database.database import engine, get_db, Base
from sqlalchemy.orm import Session
import urllib.parse


#LOAD ENV AND BIND MODELS TO ENGINE
load_dotenv()
my_api_key=os.getenv("API_KEY")
models.Base.metadata.create_all(bind = engine)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SCOPES = "openid email profile"

#subscribers pydantic model
class subscribers(BaseModel):
    email:str



#AUTOMATION PART
def get_all(db):
    gmail_users = db.query(models.Mail).filter(models.Mail.email.like('%@gmail.com')).all()
    subscribers_array = [user.email for user in gmail_users]
    mails_get = db.query(models.Mail).all()
    return subscribers_array

# Define the async scheduler job
async def job(app: FastAPI):
    http_client = app.state.http_client
    try:
        response = await http_client.get("http://localhost:8000/send")
        print("response gotten:", response)
    except Exception as e:
        print("Failed to send request to /send:", e)


# Async scheduler loop
async def run_scheduler(app: FastAPI):
    while True:
        await job(app)
        await asyncio.sleep(20)

# Use lifespan for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting async scheduler loop...")
    app.state.redis = Redis(host="localhost", port=6379)
    app.state.http_client = httpx.AsyncClient()

    #connect to the postgres server
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            cursor =conn.cursor()
            print("connection complete")
            break
        except Exception as error:
            print("connection not done",error)
            time.sleep(2)
    # Start background scheduler task
    app.state.scheduler_task = asyncio.create_task(run_scheduler(app))

    yield  # app runs here

    # Cleanup
    app.state.scheduler_task.cancel()
    await app.state.http_client.aclose()
    app.state.redis.close()
    print("App shutdown — scheduler stopped and client closed.")






#APP
# Create the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory = "frontend")
app.mount("/static", StaticFiles(directory="frontend"), name="static")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)




#ROUTES
 
@app.get("/")
def index():
    return HTMLResponse("""
    <h1>Google OAuth2 Login</h1>
    <a href="/auth">Login with Google</a>
    """)   



@app.get("/auth")
def login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@app.get("/auth/callback")
async def callback(request: Request,db:Session=Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return {"error": "Could not get access token", "details": token_data}

        # Use access token to fetch user info
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_resp.json()

    print(user_info["email"])
    print(user_info["name"])
    new_product=models.Mail(email = user_info["email"])
    db.add(new_product)
    db.commit()
    db.refresh(new_product)


    # Redirect to frontend Welcome page with username
    username = urllib.parse.quote(user_info["name"])  # Encode for URL safety
    return RedirectResponse(url=f"http://localhost:3000/welcome/{username}")



@app.get("/signup")
def get_signup_page(request:Request, response_class=HTMLResponse):
    return templates.TemplateResponse("index.html", {"request":request})


@app.post("/subscribe")
def insert_mails(email_subscriber:subscribers ,db:Session=Depends(get_db)):
    new_product=models.Mail(email = email_subscriber.email)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"added":new_product}


@app.get("/send")
def final_send(request:Request):

    redis = request.app.state.redis
    # Try to get from Redis cache
    cached = redis.get("subscribers")

    if cached:
        start = time.time()
        print("Using cached subscribers")
        subscribers = json.loads(cached.decode())
        quote = create_quotes(my_api_key)
        send_mails(quote, subscribers)
        end = time.time()
        print("total time taken: (USING CACHE)", end-start)
    else:
        start = time.time()
        print("Fetching from DB and caching")
        db = next(get_db())
        try:
            subscribers = get_all(db)
            redis.set("subscribers", json.dumps(subscribers))
            quote = create_quotes(my_api_key)
            send_mails(quote, subscribers)
        finally:
            db.close()
        end = time.time()
        print("total time taken (FROM DB AND THEN CACHING)", end-start)
    print("Email sent.")
    return {"email":"sent"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)