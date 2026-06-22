"""家庭 DIY 维修小记 — FastAPI 后端。"""

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import (
    RepairRecord,
    RepairRecordCreate,
    RepairRecordUpdate,
    RepairRecordDetail,
    Tool,
    ToolCreate,
    ToolUpdate,
    Expense,
    ExpenseCreate,
    RepairStats,
    MonthlyStat,
)

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


def row_to_expense(row) -> Expense:
    """
     * 将 SQLite Row 转为 Expense 模型。
     * @param row 数据库行
     * @returns {Expense}
     """
    return Expense(
        id=row["id"],
        record_id=row["record_id"],
        material_name=row["material_name"],
        amount=row["amount"],
        purchase_date=row["purchase_date"],
    )


@app.get("/api/records", response_model=List[RepairRecord])
def list_records() -> List[RepairRecord]:
    """获取全部维修记录。"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM repair_records ORDER BY repair_date DESC, id DESC"
        ).fetchall()
    return [row_to_record(row) for row in rows]


@app.get("/api/records/{record_id}", response_model=RepairRecordDetail)
def get_record(record_id: int) -> RepairRecordDetail:
    """获取单条维修记录（含花费列表）。"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        expense_rows = conn.execute(
            "SELECT * FROM expenses WHERE record_id = ? ORDER BY purchase_date DESC, id DESC",
            (record_id,),
        ).fetchall()
    record = row_to_record(row)
    expenses = [row_to_expense(expense_row) for expense_row in expense_rows]
    return RepairRecordDetail(**record.model_dump(), expenses=expenses)


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


def row_to_tool(row) -> Tool:
    """
     * 将 SQLite Row 转为 Tool 模型。
     * @param row 数据库行
     * @returns {Tool}
     """
    return Tool(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        remark=row["remark"],
    )


@app.get("/api/tools", response_model=List[Tool])
def list_tools() -> List[Tool]:
    """获取全部工具。"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tools ORDER BY id DESC"
        ).fetchall()
    return [row_to_tool(row) for row in rows]


@app.post("/api/tools", response_model=Tool, status_code=201)
def create_tool(payload: ToolCreate) -> Tool:
    """新建工具。"""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tools
                (name, location, remark)
            VALUES (?, ?, ?)
            """,
            (
                payload.name,
                payload.location,
                payload.remark,
            ),
        )
        conn.commit()
        tool_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM tools WHERE id = ?", (tool_id,)
        ).fetchone()
    return row_to_tool(row)


@app.put("/api/tools/{tool_id}", response_model=Tool)
def update_tool(tool_id: int, payload: ToolUpdate) -> Tool:
    """更新工具。"""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM tools WHERE id = ?", (tool_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="工具不存在")
        conn.execute(
            """
            UPDATE tools
            SET name = ?, location = ?, remark = ?
            WHERE id = ?
            """,
            (
                payload.name,
                payload.location,
                payload.remark,
                tool_id,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM tools WHERE id = ?", (tool_id,)
        ).fetchone()
    return row_to_tool(row)


@app.delete("/api/tools/{tool_id}", status_code=204)
def delete_tool(tool_id: int) -> None:
    """删除工具。"""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tools WHERE id = ?", (tool_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="工具不存在")


@app.get("/api/records/{record_id}/expenses", response_model=List[Expense])
def list_expenses(record_id: int) -> List[Expense]:
    """按维修记录编号查询花费列表。"""
    with get_connection() as conn:
        record = conn.execute(
            "SELECT id FROM repair_records WHERE id = ?", (record_id,)
        ).fetchone()
        if record is None:
            raise HTTPException(status_code=404, detail="维修记录不存在")
        rows = conn.execute(
            "SELECT * FROM expenses WHERE record_id = ? ORDER BY purchase_date DESC, id DESC",
            (record_id,),
        ).fetchall()
    return [row_to_expense(row) for row in rows]


@app.post("/api/expenses", response_model=Expense, status_code=201)
def create_expense(payload: ExpenseCreate) -> Expense:
    """新增花费。"""
    with get_connection() as conn:
        record = conn.execute(
            "SELECT id FROM repair_records WHERE id = ?", (payload.record_id,)
        ).fetchone()
        if record is None:
            raise HTTPException(status_code=404, detail="维修记录不存在")
        cursor = conn.execute(
            """
            INSERT INTO expenses
                (record_id, material_name, amount, purchase_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.record_id,
                payload.material_name,
                payload.amount,
                payload.purchase_date,
            ),
        )
        conn.commit()
        expense_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    return row_to_expense(row)


@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int) -> None:
    """删除花费。"""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM expenses WHERE id = ?", (expense_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="花费不存在")


@app.get("/api/stats/repair", response_model=RepairStats)
def get_repair_stats() -> RepairStats:
    """获取维修统计概览数据。"""
    with get_connection() as conn:
        summary_row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_count,
                COALESCE(SUM(duration_minutes), 0) AS total_duration_minutes,
                COALESCE(SUM(CASE WHEN recurred = 1 THEN 1 ELSE 0 END), 0) AS recurred_count
            FROM repair_records
            """
        ).fetchone()

        total_count = summary_row["total_count"]
        total_duration_minutes = summary_row["total_duration_minutes"]
        recurred_count = summary_row["recurred_count"]
        recurred_rate = recurred_count / total_count if total_count > 0 else 0.0

        monthly_rows = conn.execute(
            """
            SELECT
                substr(repair_date, 1, 7) AS month,
                COUNT(*) AS count
            FROM repair_records
            GROUP BY substr(repair_date, 1, 7)
            ORDER BY month DESC
            """
        ).fetchall()

        monthly_stats = [
            MonthlyStat(month=row["month"], count=row["count"])
            for row in monthly_rows
        ]

    return RepairStats(
        total_count=total_count,
        total_duration_minutes=total_duration_minutes,
        recurred_count=recurred_count,
        recurred_rate=recurred_rate,
        monthly_stats=monthly_stats,
    )
