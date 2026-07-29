from contextlib import contextmanager
from fastapi import status, FastAPI, HTTPException
import sqlite3

seed = [
    {'id':101, 'title':'R&D Phase 1','done':True},
    {'id':102, 'title':'Phase 1 Feature Implementation','done':False},
    {'id':103, 'title':'Intern Meet','done':False},
]

@contextmanager
def connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY,
                title       TEXT NOT NULL,
                done        BOOLEAN NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
            )
        """)
        
        has_rows=conn.execute("SELECT 1 FROM tasks LIMIT 1").fetchone()
        if not has_rows:
            conn.executemany("INSERT INTO tasks (id, title, done) VALUES (:id, :title, :done)",seed)
            
        
app=FastAPI()
init_db()

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
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
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