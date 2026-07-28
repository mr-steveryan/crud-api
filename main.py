from fastapi import status, FastAPI, HTTPException
import sqlite3

mem = [
    {'id':101, 'title':'R&D Phase 1','done':True},
    {'id':102, 'title':'Phase 1 Feature Implementation','done':False},
    {'id':103, 'title':'Intern Meet','done':False},
]

def connection():
    conn=sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

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
            conn.executemany("INSERT INTO tasks (id, title, done) VALUES (:id, :title, :done)",mem)
            
        
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
        return [dict(rows) for rows in records]
        
    
@app.get('/tasks/{task_id}')
def get_tasks(task_id: int):
    with connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    return dict(row)
    
@app.post("/tasks", status_code = status.HTTP_201_CREATED)
def add_task(record: dict):
    if 'title' not in record or not isinstance(record['title'],str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'title must exist and be a string')
    task_id = mem[-1]['id'] + 1
    task = {"id":task_id, "title":record['title'], "done":False}
    mem.append(task)
    return {"message": "created", "task": task}

@app.put('/tasks/{task_id}')
def update_task(task_id: int, record: dict):
    if 'title' not in record or not isinstance(record['title'],str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'title must exist and be a string')
    if 'done' not in record or not isinstance(record['done'],bool):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'done status must exist and be a boolean')
    for item in mem:
        if item['id'] == task_id:
            item['title']=record['title']
            item['done']=record['done']
            return item
    raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    
@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for item in mem:
        if item['id'] == task_id:
            mem.remove(item)
            return
    raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    