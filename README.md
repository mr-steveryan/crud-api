# task API

A minimal CRUD API built with FastAPI. Manages a list of tasks held in memory — no database, data resets on restart.

## Install & run

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn main:app --port 8000 --reload
```

Server runs at `http://localhost:8000`.

## Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/` | API info | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200 / 404 |
| POST | `/tasks` | Create task (`title` required) | 201 / 400 |
| PUT | `/tasks/{id}` | Update task (`title`, `done` required) | 200 / 400 / 404 |
| DELETE | `/tasks/{id}` | Delete task | 204 / 404 |

## API docs

Swagger UI at `http://localhost:8000/docs` (or Interactive docs at `http://localhost:8000/redoc`).

![Doc](docs/doc.png)

## Testing with curl

### `GET /` — API info

Returns basic metadata about the API.

```bash
curl -s http://localhost:8000/
```

**Response**
```json
{"name":"Task API","version":"1.0","endpoints":"[/tasks]"}
```

### `GET /health` — Health check

Confirms the server is up.

```bash
curl -s http://localhost:8000/health
```

**Response**
```json
{"status":"working"}
```

### `GET /tasks` — List all tasks

Returns every task currently in memory.

```bash
curl -s http://localhost:8000/tasks
```

**Response**
```json
[{"id":101,"title":"R&D Phase 1","done":true},{"id":102,"title":"Phase 1 Feature Implementation","done":false},{"id":103,"title":"Intern Meet","done":false},{"id":104,"title":"Client Pitch","done":true}]
```

### `GET /tasks/{id}` — Get one task

Returns a single task by id, or a 404 if it doesn't exist.

```bash
curl -s http://localhost:8000/tasks/101
```

**Response**
```json
{"id":101,"title":"R&D Phase 1","done":true}
```

```bash
curl -s http://localhost:8000/tasks/999
```

**Response**
```json
{"error":"Task 999 not found"}
```

### `POST /tasks` — Create a task

Creates a task from a `title`; rejects the request if `title` is missing or not a string.

```bash
curl -s -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Write README"}'
```

**Response**
```json
{"message":"created","task":{"id":105,"title":"Write README","done":false}}
```

```bash
curl -s -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"name": "no title"}'
```

**Response**
```json
{"error":"title should exist and should be a string"}
```

### `PUT /tasks/{id}` — Update a task

Replaces `title` and `done` on an existing task; 404 if the id doesn't exist.

```bash
curl -s -X PUT http://localhost:8000/tasks/102 \
  -H 'Content-Type: application/json' \
  -d '{"title": "Phase 1 Feature Implementation", "done": true}'
```

**Response**
```json
{"id":102,"title":"Phase 1 Feature Implementation","done":true}
```

### `DELETE /tasks/{id}` — Delete a task

Removes a task by id; 404 if it doesn't exist.

```bash
curl -s -i -X DELETE http://localhost:8000/tasks/103
```

**Response**
```
HTTP/1.1 204 No Content
```
