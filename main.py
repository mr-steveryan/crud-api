from fastapi import status, FastAPI, HTTPException
import os
import psycopg
from psycopg.rows import dict_row, DictRow
from dotenv import load_dotenv

seed = [
    {'id':101, 'title':'R&D Phase 1','done':True},
    {'id':102, 'title':'Phase 1 Feature Implementation','done':False},
    {'id':103, 'title':'Intern Meet','done':False},
]

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

def connection():
    return psycopg.Connection[DictRow].connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN DEFAULT FALSE
                )
            """)
            has_rows = cur.execute("SELECT 1 FROM tasks LIMIT 1").fetchone()
            if not has_rows:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%(title)s, %(done)s)",seed)

init_db()        
app=FastAPI()


@app.get('/')
def root():
    return {'name':'Task API','version':'1.0','endpoints':'[/tasks]'}
    
@app.get('/health')
def health():
    return {'status':'working'}

@app.get('/tasks')
def list_tasks():
    with connection() as conn:
        records = conn.execute("SELECT * FROM tasks").fetchall()
    return [dict(row) for row in records]
        
@app.get('/tasks/{task_id}')
def get_tasks(task_id: int):
    with connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    return dict(row)
    
@app.post("/tasks", status_code = status.HTTP_201_CREATED)
def add_task(record: dict):
    title = record['title']
    done = False
    if 'title' not in record or title == '':
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'title must exist and be a non-empty string')
    with connection() as conn:
        task = conn.execute("INSERT INTO tasks (title, done) VALUES (?,?) RETURNING *",(title,done)).fetchone()
    return dict(task)

@app.put('/tasks/{task_id}')
def update_task(task_id: int, record: dict):
    if 'title' not in record or not isinstance(record['title'],str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'title must exist and be a string')
    elif 'done' not in record or not isinstance(record['done'],bool):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'done status must exist and be a boolean')
    else:
        with connection() as conn:
            row = conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ? RETURNING *",(record['title'],record['done'],task_id)).fetchone()
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
        return dict(row)
            
@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with connection() as conn:
        row = conn.execute("DELETE FROM tasks WHERE id = ? RETURNING *",(task_id,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    return