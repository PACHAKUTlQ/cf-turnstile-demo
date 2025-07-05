# Cloudflare Turnstile demo

1. `git clone <repo-url>`
2. `cd <repo-directory>`
3. `uv sync`
4. `uvicorn main:app --reload`
5. Open your browser and go to `http://localhost:8000`
6. Fill out the form, don't click the turnstile captcha and submit, get the error message.
7. Fill out the form, click the turnstile captcha and submit, get the success message.