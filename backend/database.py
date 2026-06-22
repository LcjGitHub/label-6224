"""SQLite 数据库连接与初始化。"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "fixit.db"

SEED_RECORDS = [
    {
        "description": "厨房水龙头滴水，更换阀芯后恢复正常",
        "repair_date": "2025-03-12",
        "tools": "活动扳手、螺丝刀、新阀芯",
        "duration_minutes": 45,
        "recurred": 0,
    },
    {
        "description": "卧室门锁卡顿，清理锁芯并加润滑油",
        "repair_date": "2025-04-05",
        "tools": "润滑油、棉签、螺丝刀",
        "duration_minutes": 20,
        "recurred": 0,
    },
    {
        "description": "客厅灯不亮，排查发现是开关接触不良",
        "repair_date": "2025-05-18",
        "tools": "电笔、螺丝刀、新开关",
        "duration_minutes": 60,
        "recurred": 1,
    },
    {
        "description": "卫生间地漏反味，更换密封圈并清理管道",
        "repair_date": "2025-06-02",
        "tools": "密封圈、钳子、管道刷",
        "duration_minutes": 35,
        "recurred": 0,
    },
    {
        "description": "阳台推拉门轨道积灰，清理后滑动顺畅",
        "repair_date": "2025-06-15",
        "tools": "吸尘器、旧牙刷、硅基润滑脂",
        "duration_minutes": 25,
        "recurred": 0,
    },
]

SEED_TOOLS = [
    {
        "name": "活动扳手",
        "location": "工具箱第一层",
        "remark": "8寸和12寸各一把，用于拧动不同大小的螺母",
    },
    {
        "name": "十字螺丝刀套装",
        "location": "工具箱第二层",
        "remark": "PH0-PH3规格，电器维修常用",
    },
    {
        "name": "测电笔",
        "location": "工具挂板",
        "remark": "非接触式，检测电路是否带电，使用前请校验",
    },
]


def get_connection() -> sqlite3.Connection:
    """
     * 获取 SQLite 连接，启用 Row 工厂便于按列名访问。
     * @returns {sqlite3.Connection}
     """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
     * 创建维修记录表和工具表，并在空库时写入 seed 数据。
     """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repair_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                repair_date TEXT NOT NULL,
                tools TEXT NOT NULL DEFAULT '',
                duration_minutes INTEGER NOT NULL DEFAULT 0,
                recurred INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM repair_records").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO repair_records
                    (description, repair_date, tools, duration_minutes, recurred)
                VALUES
                    (:description, :repair_date, :tools, :duration_minutes, :recurred)
                """,
                SEED_RECORDS,
            )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '',
                remark TEXT NOT NULL DEFAULT ''
            )
            """
        )
        tool_count = conn.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
        if tool_count == 0:
            conn.executemany(
                """
                INSERT INTO tools
                    (name, location, remark)
                VALUES
                    (:name, :location, :remark)
                """,
                SEED_TOOLS,
            )
        conn.commit()
