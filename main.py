from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI()

class TaskSchema(BaseModel):
    id: int
    text: str = Field(min_length=1, max_length=500)
    completed: bool = False

tasks = []
tasks_id_counter = 1

@app.get("/tasks")
def get_tasks():
    return tasks or {"message": "нет задач"}

@app.post("/tasks")
def create_task(task: TaskSchema):
    global tasks_id_counter 
    new_task = TaskSchema(
        id=tasks_id_counter,
        text=task.text,
        completed=task.completed
    )
    tasks_id_counter += 1
    tasks.append(new_task)
    return {"message": "Задача добавлена", "task": new_task}

@app.put("/tasks/{id}")
def update_task(id: int, updated_task: TaskSchema):
    for task in tasks:
        if task.id == id:
            task.text = updated_task.text
            task.completed = updated_task.completed
            return {"message": "Задача обновлена", "task": task}
    return {"message": "Задача не найдена"}

@app.patch("/tasks/{id}/toggle")
def SwitchCompleted(id: int):
    for task in tasks:
        if task.id == id:
            task.completed = not task.completed
            return {"message": "Статус задачи изменен", "task": task}
    return {"message": "Задача не найдена"}

@app.delete("/tasks/{id}")
def delete_task(id: int):
    for task in tasks:
        if task.id == id:
            tasks.remove(task)
            return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)