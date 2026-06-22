"""家庭 DIY 维修小记 — FastAPI 后端。"""

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import RepairRecord, RepairRecordCreate, RepairRecordUpdate

app = FastAPI(title="FixIt API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6101", "http://127.0.0.1:6101"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """应用启动时初始化数据库。"""
    init_db()


def row_to_record(row) -> RepairRecord:
    """
     * 将 SQLite Row 转为 Pydantic 模型。
     * @param row 数据库行
     * @returns {RepairRecord}
     """
    return RepairRecord(
        id=row["id"],
        description=row["description"],
        repair_date=row["repair_date"],
        tools=row["tools"],
        duration_minutes=row["duration_minutes"],
        recurred=bool(row["recurred"]),
    )


@app.get("/api/records", response_model=List[RepairRecord])
def list_records() -> List[RepairRecord]:
    """获取全部维修记录。"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM repair_records ORDER BY repair_date DESC, id DESC"
        ).fetchall()
    return [row_to_record(row) for row in rows]


@app.get("/api/records/{record_id}", response_model=RepairRecord)
def get_record(record_id: int) -> RepairRecord:
    """获取单条维修记录。"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return row_to_record(row)


@app.post("/api/records", response_model=RepairRecord, status_code=201)
def create_record(payload: RepairRecordCreate) -> RepairRecord:
    """新建维修记录。"""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO repair_records
                (description, repair_date, tools, duration_minutes, recurred)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.description,
                payload.repair_date,
                payload.tools,
                payload.duration_minutes,
                int(payload.recurred),
            ),
        )
        conn.commit()
        record_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
    return row_to_record(row)


@app.put("/api/records/{record_id}", response_model=RepairRecord)
def update_record(record_id: int, payload: RepairRecordUpdate) -> RepairRecord:
    """更新维修记录。"""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        conn.execute(
            """
            UPDATE repair_records
            SET description = ?, repair_date = ?, tools = ?,
                duration_minutes = ?, recurred = ?
            WHERE id = ?
            """,
            (
                payload.description,
                payload.repair_date,
                payload.tools,
                payload.duration_minutes,
                int(payload.recurred),
                record_id,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
    return row_to_record(row)


@app.delete("/api/records/{record_id}", status_code=204)
def delete_record(record_id: int) -> None:
    """删除维修记录。"""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM repair_records WHERE id = ?", (record_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")
