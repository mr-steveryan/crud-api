from fastapi import FastAPI, HTTPException, status

mem = [
    {'id':101, 'title':'R&D Phase 1','done':True},
    {'id':102, 'title':'Phase 1 Feature Implementation','done':False},
    {'id':103, 'title':'Intern Meet','done':False},
    {'id':104, 'title':'Client Pitch','done':True}
]

app=FastAPI()

@app.get('/')
def root():
    return {'name':'Task API','version':'1.0','endpoints':'[/tasks]'}
    
@app.get('/health')
def health():
    return {'status':'working'}

@app.get('/tasks')
def list_tasks():
    return mem
    
@app.get('/tasks/{task_id}')
def get_tasks(task_id: int):
    for item in mem:
        if item['id'] == task_id:
            return item
    raise HTTPException(status.HTTP_404_NOT_FOUND, f'Task {task_id} not found')
    
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
    