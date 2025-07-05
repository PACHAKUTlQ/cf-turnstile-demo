from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx # For making HTTP requests to Cloudflare
import os

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Cloudflare Turnstile keys for local testing
# Use the "Always passes visible" sitekey for the frontend
CLOUDFLARE_TURNSTILE_SITE_KEY = "3x00000000000000000000FF" # [1]
# Use the "Always passes" secret key for the backend validation
CLOUDFLARE_TURNSTILE_SECRET_KEY = "1x0000000000000000000000000000000AA" # [1]

# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cloudflare_turnstile_site_key": CLOUDFLARE_TURNSTILE_SITE_KEY
    })

# Handle form submission and validate Turnstile
@app.post("/submit")
async def submit_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    cf_turnstile_response: str = Form(..., alias="cf-turnstile-response") # Get the Turnstile token
):
    # Verify the Turnstile token with Cloudflare
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": CLOUDFLARE_TURNSTILE_SECRET_KEY,
                "response": cf_turnstile_response,
                "remoteip": request.client.host # Optional: include user's IP for better analysis
            }
        )
        turnstile_verification_result = response.json()

    if turnstile_verification_result.get("success"):
        return {"message": f"Success! Hello {name}. Your email is {email}. Turnstile verification passed!", "status": "success"}
    else:
        # Get error codes for debugging
        error_codes = turnstile_verification_result.get("error-codes", ["Unknown error"])
        return {"message": f"Error! Turnstile verification failed. Error codes: {', '.join(error_codes)}", "status": "error"}