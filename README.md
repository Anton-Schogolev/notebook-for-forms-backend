# Notebook for Forms Backend

Requires Python 3.12+, uv, and Docker Compose. Run commands from the project root.

## Development

1. Install dependencies: `uv sync`.
2. Copy `.env.example` to `.env` if needed, then set local credentials. Keep
   `DATABASE_URL` consistent with `POSTGRES_*`; URL-encode special characters.
3. Start PostgreSQL: `docker compose up -d --wait db`.
4. Start FastAPI with `uv run dev` or `uv run fastapi dev`.

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

## Auth API tests

Run from the project root with Docker running and `uv` installed.

```bash
uv run test
```

The command runs pytest in quiet mode, starts a dedicated PostgreSQL 18 container
on port 55432, and removes it when the run ends, even if tests fail. Each case
rolls back its database transaction. To pass your own pytest options, run the
script directly, for example `./scripts/test -k login`.

### Keep the test database running

For repeated test runs, add the test database URL to `.env` and start the
dedicated PostgreSQL container once.

```dotenv
TEST_DATABASE_URL=postgresql+psycopg://notebook_auth_test:notebook_auth_test@127.0.0.1:55432/notebook_auth_test
```

```bash
docker compose -f tests/compose.yaml up -d --wait
```

Run the tests from the project root as often as needed. Each test rolls back
its database changes.

```bash
uv run python -m pytest tests
```

Remove the test container when you're done.

```bash
docker compose -f tests/compose.yaml down
```
