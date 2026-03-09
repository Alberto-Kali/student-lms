# python-backend

FastAPI backend for LMS with ClickHouse storage.

## Run locally

1. `docker compose up --build`
2. API docs: `http://localhost:8000/docs`

## API (initial)

- `GET /healthz` - health + ClickHouse ping
- `GET /api/v1/lms/courses` - list LMS courses
- `POST /api/v1/visit/lead` - accept lead from visit frontend
- `GET /api/v1/visit/content` - reserved stub endpoint for visit frontend
