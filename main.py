from fastapi import FastAPI, Depends
from typing import Annotated
from pydantic import BaseModel, Field
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import select

app = FastAPI()
engine = create_async_engine("sqlite+aiosqlite:///./ToDoList.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session
sessiondep = Annotated[AsyncSession, Depends(get_session)]

Base = declarative_base()

class TaskModel(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    completed: Mapped[bool] = mapped_column(default=False)

class TaskAddSchema(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    completed: bool = False

class TaskSchema(TaskAddSchema):
    id: int

@app.get("/tasks")
async def get_tasks(session: sessiondep):
    result = await session.execute(select(TaskModel))
    tasks = result.scalars().all()
    return tasks or {"message": "нет задач"}

@app.post("/tasks")
async def create_task(task: TaskAddSchema, session: sessiondep):
    new_task = TaskModel(text=task.text, completed=task.completed)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return {"message": "Задача добавлена", "task": new_task}

@app.put("/tasks/{id}")
async def update_task(id: int, updated_task: TaskAddSchema, session: sessiondep):
    task = await session.get(TaskModel, id)
    if not task:
        return {"message": "Задача не найдена"}
    task.text = updated_task.text
    task.completed = updated_task.completed
    await session.commit()
    await session.refresh(task)
    return {"message": "Задача обновлена", "task": task}

@app.patch("/tasks/{id}/toggle")
async def switch_completed(id: int, session: sessiondep):
    task = await session.get(TaskModel, id)
    if not task:
        return {"message": "Задача не найдена"}
    task.completed = not task.completed
    await session.commit()
    await session.refresh(task)
    return {"message": "Статус задачи изменен", "task": task}

@app.delete("/tasks/{id}")
async def delete_task(id: int, session: sessiondep):
    task = await session.get(TaskModel, id)
    if not task:
        return {"message": "Задача не найдена"}
    await session.delete(task)
    await session.commit()
    return {"message": "Задача удалена"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
