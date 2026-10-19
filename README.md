# Kiwi-Biz Assistant

A multi-tenant, AI-powered document management and Q&A platform for New Zealand small and medium businesses. 

Upload your policies, contracts, HR, and other business documents, then ask questions in plain English and get answers with source citations.

Built as the capstone for **COMPX576-26B: Programming Project** at the University of Waikato, supervised by Dr. Sapna Jaidka.

---

## Features

- **Document Q&A (RAG):** ask questions across your company's documents; answers are generated from the most relevant passages and include source citations.
- **Multi-turn chat:** conversation history is saved and shown in a sidebar.
- **Document management:** drag-and-drop upload with real progress, categories (Policy, Contract, Financial, HR, Other), category filtering, and an in-app viewer.
- **Supported file types:** PDF, DOCX, TXT, CSV.
- **Multi-tenancy:** every company only sees its own documents and conversations.
- **Role-based access control:** `super_admin`, `admin` and `staff` roles with role-based permissions (for example, who can delete documents).
- **Subscriptions:** companies have a plan (free, premium monthly, elite yearly) that a Super Admin can enable, disable or expire.
- **Login-As (impersonation):** Super Admins can temporarily act as another user (30-minute token with an audit claim and an exit banner).
- **Admin stats dashboard:** document counts by category, upload activity over time, and Q&A usage.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Pinia, Vue Router, Tailwind CSS v4, Chart.js (vue-chartjs) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + pgvector, SQLAlchemy, Alembic |
| File storage | AWS S3 / Azure Blob Storage, with a local fallback for development |
| AI | OpenAI `text-embedding-3-small` (embeddings), `gpt-4o-mini` (answers) |
| Auth | JWT with RBAC |
| Hosting | Azure Container Apps, Azure Container Registry, Azure PostgreSQL Flexible Server, Azure Static Web Apps |

## How it works

1. A user uploads a document. The backend extracts the text, splits it into chunks (1000 characters with 150 overlap), creates an embedding for each chunk, and stores them in PostgreSQL using pgvector (IVFFlat cosine index).
2. When a user asks a question, the question is embedded and the closest chunks are retrieved by cosine similarity, **scoped to the user's company**.
3. The retrieved chunks and the conversation history are sent to `gpt-4o-mini`, which writes the answer.
4. The answer is returned with citations pointing back to the source documents.

## Project structure

```
kiwibiz-assistant/
├── backend/        # FastAPI app, models, Alembic migrations, RAG pipeline
└── frontend/       # Vue 3 app (views, components, Pinia stores, API client)
```

> Adjust folder names above if your repo layout differs.

## Getting started (local development)

### Prerequisites

- Python 3.13
- Node.js (v26+ was used in development)
- Docker Desktop (for PostgreSQL with pgvector)
- An OpenAI API key

### 1. Database

Start PostgreSQL with pgvector in Docker (Docker Desktop must be running first):

```bash
docker start kiwi-biz-db
```

The database listens on port `5432`.

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your values
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

The API runs at http://localhost:8001 (interactive docs at `/docs`).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at http://localhost:5173 (or 5174 if that port is busy).

## Configuration

Create `backend/.env` with values like these (names may differ slightly, so check `.env.example`):

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db>
OPENAI_API_KEY=<your key>
JWT_SECRET=<a long random string>
STORAGE_BACKEND=local          # or s3 / azure
```

Never commit your `.env` file or any API keys.

## Database migrations

```bash
alembic revision -m "describe the change"   # create a migration
alembic upgrade head                        # apply migrations
```

Notes:
- New SQLAlchemy models must be imported in the metadata/base module so Alembic can detect them.
- Alembic autogenerate does not create Postgres enum types. Add the `CREATE TYPE` step to the migration by hand.
- `bcrypt` is pinned to `4.0.1` for compatibility with `passlib 1.7.4`.

## Testing

- End-to-end manual testing of each feature across the different roles.
- Browser automation with Selenium.

## Design

- **Colours:** harbour teal `#1B6F63`, manuka amber `#E8A33D`, deep pine `#0F1E1C`, warm paper `#F7F5F0`, sand `#DCD6C9`
- **Fonts:** Fraunces (display), Inter (body), JetBrains Mono (data)

## Deployment

The backend runs as a Docker image on Azure Container Apps (image stored in Azure Container Registry), backed by Azure PostgreSQL Flexible Server with pgvector and Azure Blob Storage. The Vue frontend is deployed to Azure Static Web Apps through GitHub.

## Author

Dhruba Khanal, Master of Information Technology, University of Waikato.

## License

This project was created for academic purposes.
