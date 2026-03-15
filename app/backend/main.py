"""
TaskFlow API — Task Management Service
========================================
Backend API for the TaskFlow task management application.

NOTE FOR EVALUATORS (DO NOT SHARE WITH CANDIDATES):
This application contains 15+ intentional bugs across different categories.
See docs/BUGS_INTERNAL.md for the complete list.
"""

import os
import json
import uuid
import sqlite3
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─── Configuration ───────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "taskflow.db")
ENV = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="TaskFlow API",
    version="1.2.0",
    description="Task management API for teams",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Database ────────────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'member', 'viewer')),
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                owner_id TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'deleted')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                project_id TEXT NOT NULL,
                assignee_id TEXT,
                reporter_id TEXT NOT NULL,
                status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'in_review', 'done', 'cancelled')),
                priority TEXT DEFAULT 'medium' CHECK(priority IN ('critical', 'high', 'medium', 'low')),
                due_date TEXT,
                tags TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (assignee_id) REFERENCES users(id),
                FOREIGN KEY (reporter_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                author_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (author_id) REFERENCES users(id)
            );
        """)
        conn.commit()


init_db()


# ─── Models ──────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str
    full_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = "member"


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    owner_id: str


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    reporter_id: str
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None
    tags: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None


class CommentCreate(BaseModel):
    task_id: str
    author_id: str
    content: str = Field(..., min_length=1)


# ─── Helper ──────────────────────────────────────────────────────
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    if "tags" in d and isinstance(d["tags"], str):
        try:
            d["tags"] = json.loads(d["tags"])
        except:
            d["tags"] = []
    return d


# ─── Health ──────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "version": "1.2.0", "environment": ENV}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/users", status_code=201)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    now = now_iso()

    # 🐛 BUG #1: No email validation — accepts "notanemail" as valid email
    # (Missing regex or proper email validation)

    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id, username, email, full_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, user.username, user.email, user.full_name, user.role, now),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise HTTPException(status_code=409, detail="Username already exists")
            elif "email" in str(e):
                raise HTTPException(status_code=409, detail="Email already exists")
            raise HTTPException(status_code=400, detail=str(e))

    return {"id": user_id, "username": user.username, "email": user.email,
            "full_name": user.full_name, "role": user.role, "created_at": now}


@app.get("/api/users")
async def list_users(active_only: bool = True):
    with get_db() as conn:
        if active_only:
            rows = conn.execute("SELECT * FROM users WHERE is_active = 1").fetchall()
        else:
            rows = conn.execute("SELECT * FROM users").fetchall()
    return {"users": [dict(r) for r in rows], "total": len(rows)}


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        # 🐛 BUG #2: Soft delete doesn't actually work — sets is_active but
        # tasks assigned to this user still show them as assignee
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
        conn.commit()

    return {"message": "User deactivated"}


# ═══════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/projects", status_code=201)
async def create_project(project: ProjectCreate):
    project_id = str(uuid.uuid4())
    now = now_iso()

    # 🐛 BUG #3: No validation that owner_id exists in users table
    with get_db() as conn:
        conn.execute(
            "INSERT INTO projects (id, name, description, owner_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, project.name, project.description, project.owner_id, now, now),
        )
        conn.commit()

    return {"id": project_id, "name": project.name, "description": project.description,
            "owner_id": project.owner_id, "status": "active", "created_at": now}


@app.get("/api/projects")
async def list_projects(status: Optional[str] = None):
    with get_db() as conn:
        if status:
            rows = conn.execute("SELECT * FROM projects WHERE status = ?", (status,)).fetchall()
        else:
            # 🐛 BUG #4: Shows deleted projects in default listing
            # Should filter out status = 'deleted' by default
            rows = conn.execute("SELECT * FROM projects").fetchall()
    return {"projects": [dict(r) for r in rows], "total": len(rows)}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(row)


@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, data: dict):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        allowed = ["name", "description", "status"]
        updates = {k: v for k, v in data.items() if k in allowed}
        updates["updated_at"] = now_iso()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [project_id]

        conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        conn.commit()

        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row)


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        # 🐛 BUG #5: Deleting a project doesn't handle associated tasks
        # Tasks remain orphaned pointing to a deleted project
        conn.execute("UPDATE projects SET status = 'deleted', updated_at = ? WHERE id = ?",
                      (now_iso(), project_id))
        conn.commit()

    return {"message": "Project deleted"}


# ═══════════════════════════════════════════════════════════════
# TASKS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/tasks", status_code=201)
async def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())
    now = now_iso()

    with get_db() as conn:
        # Validate project exists
        project = conn.execute("SELECT * FROM projects WHERE id = ?", (task.project_id,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 🐛 BUG #6: Allows creating tasks in archived/deleted projects
        # Should check project.status == 'active'

        # 🐛 BUG #7: No validation that reporter_id exists
        # (assignee_id can be null, but reporter_id should be validated)

        tags_json = json.dumps(task.tags or [])

        conn.execute(
            """INSERT INTO tasks (id, title, description, project_id, assignee_id,
               reporter_id, priority, due_date, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, task.title, task.description, task.project_id, task.assignee_id,
             task.reporter_id, task.priority, task.due_date, tags_json, now, now),
        )
        conn.commit()

    return {
        "id": task_id, "title": task.title, "description": task.description,
        "project_id": task.project_id, "assignee_id": task.assignee_id,
        "reporter_id": task.reporter_id, "status": "todo", "priority": task.priority,
        "due_date": task.due_date, "tags": task.tags or [], "created_at": now,
    }


@app.get("/api/tasks")
async def list_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    conditions = []
    params = []

    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if assignee_id:
        conditions.append("assignee_id = ?")
        params.append(assignee_id)
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    if search:
        # 🐛 BUG #8: SQL Injection vulnerability — search is not parameterized
        conditions.append(f"(title LIKE '%{search}%' OR description LIKE '%{search}%')")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    offset = (page - 1) * page_size

    with get_db() as conn:
        # 🐛 BUG #9: Pagination — total count doesn't respect filters
        total_row = conn.execute("SELECT COUNT(*) as total FROM tasks").fetchone()
        total = total_row["total"]

        rows = conn.execute(
            f"SELECT * FROM tasks{where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

    tasks = [row_to_dict(r) for r in rows]

    return {
        "tasks": tasks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_dict(row)


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, data: TaskUpdate):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        current = dict(row)
        updates = {}

        if data.title is not None:
            updates["title"] = data.title
        if data.description is not None:
            updates["description"] = data.description
        if data.assignee_id is not None:
            updates["assignee_id"] = data.assignee_id
        if data.priority is not None:
            updates["priority"] = data.priority
        if data.due_date is not None:
            updates["due_date"] = data.due_date
        if data.tags is not None:
            updates["tags"] = json.dumps(data.tags)

        if data.status is not None:
            # 🐛 BUG #10: Invalid state transitions allowed
            # e.g., can go from "done" back to "todo", or "cancelled" to "in_progress"
            # Should enforce: todo -> in_progress -> in_review -> done
            #                 any state -> cancelled (one way)
            updates["status"] = data.status

        if not updates:
            return row_to_dict(row)

        updates["updated_at"] = now_iso()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [task_id]

        conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        conn.commit()

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    return row_to_dict(row)


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        # 🐛 BUG #11: Hard delete instead of soft delete — loses audit trail
        # Also doesn't delete associated comments
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

    # 🐛 BUG #12: Returns 200 instead of 204 No Content for DELETE
    return {"message": "Task deleted"}


# ═══════════════════════════════════════════════════════════════
# COMMENTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/tasks/{task_id}/comments", status_code=201)
async def create_comment(task_id: str, comment: CommentCreate):
    comment_id = str(uuid.uuid4())
    now = now_iso()

    with get_db() as conn:
        # Check task exists
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # 🐛 BUG #13: comment.task_id from body might differ from URL task_id
        # Uses comment.task_id instead of the URL parameter
        conn.execute(
            "INSERT INTO comments (id, task_id, author_id, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (comment_id, comment.task_id, comment.author_id, comment.content, now),
        )
        conn.commit()

    return {"id": comment_id, "task_id": comment.task_id, "author_id": comment.author_id,
            "content": comment.content, "created_at": now}


@app.get("/api/tasks/{task_id}/comments")
async def list_comments(task_id: str):
    with get_db() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        rows = conn.execute(
            "SELECT * FROM comments WHERE task_id = ? ORDER BY created_at ASC",
            (task_id,),
        ).fetchall()

    return {"comments": [dict(r) for r in rows], "total": len(rows)}


# ═══════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/stats")
async def get_stats(project_id: Optional[str] = None):
    with get_db() as conn:
        if project_id:
            cond = " WHERE project_id = ?"
            params = (project_id,)
        else:
            cond = ""
            params = ()

        total = conn.execute(f"SELECT COUNT(*) as c FROM tasks{cond}", params).fetchone()["c"]
        by_status = conn.execute(
            f"SELECT status, COUNT(*) as count FROM tasks{cond} GROUP BY status", params
        ).fetchall()
        by_priority = conn.execute(
            f"SELECT priority, COUNT(*) as count FROM tasks{cond} GROUP BY priority", params
        ).fetchall()

        # 🐛 BUG #14: Overdue calculation is wrong — compares date strings incorrectly
        # Uses string comparison which breaks with different date formats
        overdue = conn.execute(
            f"SELECT COUNT(*) as c FROM tasks{cond} AND due_date < ? AND status NOT IN ('done', 'cancelled')"
            if cond else
            f"SELECT COUNT(*) as c FROM tasks WHERE due_date < ? AND status NOT IN ('done', 'cancelled')",
            params + (datetime.now(timezone.utc).strftime("%Y-%m-%d"),) if project_id
            else (datetime.now(timezone.utc).strftime("%Y-%m-%d"),),
        ).fetchone()["c"]

    return {
        "total_tasks": total,
        "by_status": {r["status"]: r["count"] for r in by_status},
        "by_priority": {r["priority"]: r["count"] for r in by_priority},
        "overdue": overdue,
    }


# ═══════════════════════════════════════════════════════════════
# BULK OPERATIONS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/tasks/bulk-update")
async def bulk_update_tasks(data: dict):
    task_ids = data.get("task_ids", [])
    updates = data.get("updates", {})

    if not task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")

    allowed = ["status", "priority", "assignee_id"]
    filtered = {k: v for k, v in updates.items() if k in allowed}

    if not filtered:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    filtered["updated_at"] = now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in filtered)
    values = list(filtered.values())

    # 🐛 BUG #15: No transaction — partial updates possible if one fails
    # Also no validation that all task_ids exist
    with get_db() as conn:
        updated = 0
        for tid in task_ids:
            cursor = conn.execute(
                f"UPDATE tasks SET {set_clause} WHERE id = ?",
                values + [tid],
            )
            updated += cursor.rowcount
        conn.commit()

    # 🐛 BUG #16: Returns 200 even if some task_ids didn't exist
    # 'updated' count may be less than len(task_ids) but no error
    return {"message": f"Updated {updated} tasks", "updated": updated}


# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════

@app.get("/api/export/tasks")
async def export_tasks(project_id: Optional[str] = None, format: str = "json"):
    with get_db() as conn:
        if project_id:
            rows = conn.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks").fetchall()

    tasks = [row_to_dict(r) for r in rows]

    if format == "csv":
        if not tasks:
            return JSONResponse(content="", media_type="text/csv")

        headers = tasks[0].keys()
        lines = [",".join(headers)]
        for t in tasks:
            # 🐛 BUG #17: CSV export doesn't escape commas or quotes in content
            line = ",".join(str(t.get(h, "")) for h in headers)
            lines.append(line)

        return JSONResponse(content="\n".join(lines), media_type="text/csv")

    return {"tasks": tasks, "total": len(tasks)}


# ─── Frontend serving ────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("frontend/index.html")


# ─── Entry Point ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
