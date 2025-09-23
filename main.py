from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI()

class TaskSchema(BaseModel):
    id: int
    text: str = Field(min_length=1, max_length=500)
    completed: bool = False

tasks = []



@app.get("/tasks")
def get_tasks():
    return tasks or {"message": "нет задач"}

@app.post("/tasks")
def create_task(task: TaskSchema):
    task.id = tasks_id_counter
    tasks_id_counter += 1
    tasks.append(task)
    return {"message": "Задача добавлена"}

@app.delete(f"/tasks/{id}")
def delete_task(id: int):
    for task in tasks:
        if task.id == id:
            tasks.pop(id)
            return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)