from fastapi import FastAPI

app = FastAPI(title="python-backend")


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok', 'backend': 'python-fastapi'}
