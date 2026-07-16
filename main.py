from fastapi import FastAPI
from fastapi.responses import JSONResponse

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
    return JSONResponse(
        status_code=404,
        content={'error':f'Task {task_id} not found'}
    )
    
@app.post("/tasks", status_code = 201)
def add_task(record: dict):
    if 'title' not in record or not isinstance(record['title'],str):
        return JSONResponse(
            status_code=400,
            content={'error':'title should exist and should be a string'}
        )
    task_id = mem[-1]['id'] + 1
    task = {"id":task_id, "title":record['title'], "Done":False}
    mem.append(task)
    return {"message": "created", "task": task}

@app.put('/tasks/{task_id}')
def update_task(task_id: int, record: dict):
    if 'title' not in record or not isinstance(record['title'],str):
        return JSONResponse(
            status_code=400,
            content={'error':'title should exist and should be a string'}
        )
    if 'done' not in record or not isinstance(record['done'],bool):
        return JSONResponse(
            status_code=400,
            content={'error':'done should exist and should be a boolean'}
        )
    for item in mem:
        if item['id'] == task_id:
            item['title']=record['title']
            item['done']=record['done']
            return item
    return JSONResponse(
        status_code=404,
        content={'error':f"record with id: {task_id} doesn't exist"}
    )
    
@app.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int):
    for item in mem:
        if item['id'] == task_id:
            mem.remove(item)
            return
    return JSONResponse(
        status_code=404,
        content={'error':f"record with id: {task_id} doesn't exist"}
    )
    