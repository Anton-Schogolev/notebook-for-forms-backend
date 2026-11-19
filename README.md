# Notebook for Forms Backend

Requires Python 3.12+, uv, and Docker Compose. Run commands from the project root.

## Development

1. Install dependencies: `uv sync`.
2. Copy `.env.example` to `.env` if needed, then set local credentials. Keep
   `DATABASE_URL` consistent with `POSTGRES_*`; URL-encode special characters.
3. Start PostgreSQL: `docker compose up -d --wait db`.
4. Start FastAPI: `uv run fastapi dev`.

PostgreSQL 18 runs in Docker at `localhost:5432`; FastAPI runs locally.
The application uses an async Psycopg engine and SQLModel sessions. Import
`SessionDep` from `src.dependencies.database` in async routes and await database
operations. Sessions are closed after each request; writes must be committed
explicitly. The engine's connection pool is disposed when the application shuts
down. Tables and migrations are not yet configured.

## Database commands

```bash
docker compose ps       # Status and health
docker compose logs db  # Logs
docker compose stop db  # Stop database
docker compose down     # Remove containers; keep database data
```

Data persists in a named volume. `docker compose down -v` deletes it.
`POSTGRES_*` settings initialize an empty volume only; editing `.env` does not
change existing database credentials. Changing PostgreSQL major versions requires
a database migration.
