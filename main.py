# main.py
import os

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from starlette.requests import Request
import uvicorn
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

app = FastAPI()

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_SCOPE = "user-library-read user-read-private user-read-email"

# FastAPI OAuth2 configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/login",
    tokenUrl="/token",
)

# Spotipy configuration
sp_oauth = SpotifyOAuth(
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    scope=SPOTIPY_SCOPE,
)

# Mock database to store user tokens
fake_db = {}


def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and fetch user information from Spotify API
    sp = spotipy.Spotify(auth=token)
    user_info = sp.me()
    return user_info


@app.get("/login")
async def login(request: Request):
    # Generate the Spotify authorization URL
    auth_url = sp_oauth.get_authorize_url()
    # Redirect the user to the Spotify authorization URL
    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(code: str):
    # Retrieve the access token using the authorization code
    print("hello")
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info["access_token"]
    # Store the access token in the fake database (you might want to use a real database in production)
    fake_db["access_token"] = access_token
    # Redirect the user to the "/me" route
    return RedirectResponse("/me")


@app.get("/me", response_model=dict)
async def read_me(current_user: dict = Depends(get_current_user)):
    # Return user information fetched from the Spotify API
    return current_user


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
