# student-lms / main

Stable production branch.

## Branches

Service branches:
- `lms-frontend` (Bun + Vite + Vue)
- `visit-frontend` (Bun + Vite + Vue)
- `python-backend` (FastAPI)
- `haskell-backend` (Stack + Servant)

Integration branches:
- `dev` = `lms-frontend` + `visit-frontend` + `python-backend`
- `preproduction` = `lms-frontend` + `visit-frontend` + `haskell-backend`

Release flow:
- promote `dev` -> `preproduction`
- promote stable `preproduction` -> `main`
