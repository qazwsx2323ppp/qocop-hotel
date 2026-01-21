import mysql.connector
from mysql.connector import errorcode
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as pt

from config import config
from dotenv import load_dotenv

# 1) 强制从项目根目录加载 .env（以 controller.py 所在目录为基准）
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# 2) 读取并校验（缺失就立刻报错，避免悄悄连错账号）
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_USER:
    raise RuntimeError(f"DB_USER 未设置或 .env 未加载成功：{ENV_PATH}")
if DB_PASSWORD is None or DB_PASSWORD == "":
    raise RuntimeError(f"DB_PASSWORD 未设置或为空：{ENV_PATH}")

# ===================SQL Connectivity=================
connection = mysql.connector.connect(
    host=config.get("DB_HOST"),
    user=DB_USER,
    password=DB_PASSWORD,
    database=config.get("DB_NAME"),
    port=3306,  # 用 int 更规范
    autocommit=config.get("DB_AUTOCOMMIT"),
)

cursor = connection.cursor(buffered=True)

# SQL functions


def _column_type(table: str, column: str) -> str:
    cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s;", (column,))
    row = cursor.fetchone()
    return str(row[1]).lower() if row else ""


def _column_nullable(table: str, column: str) -> bool:
    cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s;", (column,))
    row = cursor.fetchone()
    if not row:
        return True
    # Field, Type, Null, Key, Default, Extra
    return str(row[2]).strip().upper() != "NO"


def require_prefixed_id_schema():
    checks = [
        ("guests", "id"),
        ("rooms", "id"),
        ("reservations", "id"),
        ("reservations", "g_id"),
        ("reservations", "r_id"),
    ]
    for table, column in checks:
        col_type = _column_type(table, column)
        if "varchar" not in col_type:
            raise RuntimeError(
                f"数据库结构不匹配：`{table}`.`{column}` 需要是 VARCHAR(带前缀ID，如 guest_1/room_1/res_1)。"
                f"请重新导入 `sql/hms.sql`（会重建表），或手动迁移现有表结构。当前类型：{col_type!r}"
            )

    # 业务约束：预订必须关联住客与房间（避免 g_id/r_id 为空导致“无客/无房”记录）
    for table, column in [("reservations", "g_id"), ("reservations", "r_id")]:
        if not _column_nullable(table, column):
            continue

        cursor.execute(
            f"SELECT COUNT(*) FROM `{table}` WHERE `{column}` IS NULL;"
        )
        null_count = int(cursor.fetchone()[0] or 0)
        if null_count != 0:
            raise RuntimeError(
                f"数据库结构不匹配：`{table}`.`{column}` 需要为 NOT NULL（业务要求预订必须关联住客/房间）。"
                f"但当前表中存在 {null_count} 条 `{column}` 为 NULL 的记录，无法自动迁移。"
                f"请清理数据后重新导入 `sql/hms.sql`（会重建表），或手动迁移现有表结构。"
            )

        try:
            cursor.execute(
                f"""ALTER TABLE `{table}`
                MODIFY `{column}` varchar(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL;"""
            )
        except mysql.connector.Error as err:
            raise RuntimeError(
                f"数据库结构不匹配：`{table}`.`{column}` 需要为 NOT NULL，且自动迁移失败：{err}。"
                f"请重新导入 `sql/hms.sql`（会重建表），或手动迁移现有表结构。"
            ) from err

        if _column_nullable(table, column):
            raise RuntimeError(
                f"数据库结构不匹配：`{table}`.`{column}` 自动迁移后仍为可空。"
                f"请重新导入 `sql/hms.sql`（会重建表），或手动迁移现有表结构。"
            )


require_prefixed_id_schema()


def normalize_prefixed_id(value, prefix: str):
    """
    Accept either a pure numeric id (e.g. "12") or a prefixed id (e.g. "res_12").
    Returns a normalized prefixed id string, or None if invalid.
    """
    text = str(value).strip() if value is not None else ""
    if not text:
        return None
    if text.startswith(prefix):
        suffix = text[len(prefix) :]
        return text if suffix.isdigit() else None
    return f"{prefix}{text}" if text.isdigit() else None


def _next_prefixed_id(table: str, prefix: str) -> str:
    cursor.execute(
        f"""
        SELECT id
        FROM {table}
        WHERE id LIKE %s
        ORDER BY CAST(SUBSTRING_INDEX(id, '_', -1) AS UNSIGNED) DESC
        LIMIT 1;
        """,
        (f"{prefix}%",),
    )
    row = cursor.fetchone()
    if not row or not row[0]:
        return f"{prefix}1"
    last_id = str(row[0])
    try:
        last_num = int(last_id.split("_")[-1])
    except Exception:
        last_num = 0
    return f"{prefix}{last_num + 1}"


def parse_datetime_input(value, *, allow_empty: bool):
    """
    Parse GUI input into datetime / None.

    Accepted:
    - "now" (case-insensitive) -> datetime.now()
    - "YYYY-MM-DD"
    - "YYYY-MM-DD HH:MM"
    - "YYYY-MM-DD HH:MM:SS"
    - empty: None if allow_empty else error
    """
    text = str(value).strip() if value is not None else ""
    if text == "":
        return (None, None) if allow_empty else (None, "required")

    if text.lower() == "now":
        return datetime.now(), None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt), None
        except ValueError:
            continue
    return None, "invalid_datetime"


def room_status_from_reservation_states(states):
    if not states:
        return "可预订"
    if any(s == "进行中" for s in states):
        return "使用中"
    if any(s == "已预订" for s in states):
        return "已预订"
    return "可预订"


def checkUser(username, password=None):
    cursor.execute(
        "SELECT COUNT(username) FROM login WHERE username = %s AND BINARY password = %s;",
        (username, password),
    )
    return cursor.fetchone()[0] >= 1


def human_format(num):
    if num < 1000:
        return num

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000
    return "%.1f%s" % (num, ["", "K", "M", "G", "T", "P"][magnitude])


def updatePassword(username, sec_ans, sec_que, password):
    cursor.execute(
        "UPDATE login SET password = %s WHERE username = %s AND sec_ans = %s AND sec_que = %s LIMIT 1;",
        (password, username, sec_ans, sec_que),
    )
    cursor.execute(
        "SELECT COUNT(username) FROM login WHERE username = %s AND BINARY password = %s AND sec_ans = %s AND sec_que = %s;",
        (username, password, sec_ans, sec_que),
    )
    return cursor.fetchone()[0] >= 1


def updateUsername(oldusername, password, newusername):
    cursor.execute(
        "UPDATE login SET username = %s WHERE username = %s AND BINARY password = %s LIMIT 1;",
        (newusername, oldusername, password),
    )
    cursor.execute(
        "SELECT COUNT(username) FROM login WHERE username = %s AND BINARY password = %s;",
        (newusername, password),
    )
    return cursor.fetchone()[0] >= 1



def find_g_id(name):
    cursor.execute("select id from guests where name = %s;", (name,))
    rows = cursor.fetchall() if cursor.rowcount else []
    if len(rows) != 1:
        return None
    return rows[0][0]


def checkin(g_id):
    guest_id = normalize_prefixed_id(g_id, "guest_") or str(g_id).strip()
    cursor.execute("SELECT id FROM reservations WHERE g_id = %s LIMIT 1;", (guest_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE reservations SET check_in = current_timestamp WHERE g_id = %s;",
            (guest_id,),
        )
        return "successful"
    return "No reservations for the given Guest"



def checkout(id):
    reservation_id = normalize_prefixed_id(id, "res_") or str(id).strip()
    cursor.execute(
        "UPDATE reservations SET check_out = current_timestamp WHERE id = %s LIMIT 1;",
        (reservation_id,),
    )
    if cursor.rowcount == 0:
        return False
    return True


# ============Python Functions==========


def acceptable(*args, acceptables):
    """
    If the characters in StringVars passed as arguments are in acceptables return True, else returns False
    """
    for arg in args:
        for char in arg:
            if char.lower() not in acceptables:
                return False
    return True



# Get all guests
def get_guests():
    cmd = "select id, name, address, email_id, phone, created_at from guests;"
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return False
    return cursor.fetchall()


# Add a guest
def add_guest(name, address, email_id, phone):
    try:
        phone_int = int(str(phone).strip())
    except Exception:
        return False, "invalid_phone"

    guest_id = _next_prefixed_id("guests", "guest_")
    cmd = "insert into guests(id,name,address,email_id,phone) values(%s,%s,%s,%s,%s);"
    try:
        cursor.execute(cmd, (guest_id, name, address, email_id, phone_int))
    except mysql.connector.Error:
        return False, "db_error"

    if cursor.rowcount == 0:
        return False, "db_error"
    return True, None


# add a room
def add_room(room_no, price, room_type):
    try:
        cursor.execute("SELECT COUNT(id) FROM rooms WHERE room_no = %s;", (room_no,))
        if cursor.fetchone()[0] > 0:
            return False, "duplicate_room_no"
    except mysql.connector.Error:
        pass

    room_id = _next_prefixed_id("rooms", "room_")
    cmd = "insert into rooms(id,room_no,price,room_type,status) values(%s,%s,%s,%s,%s);"
    try:
        cursor.execute(cmd, (room_id, room_no, price, room_type, "可预订"))
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            return False, "duplicate_room_no"
        return False, "db_error"
    if cursor.rowcount == 0:
        return False, "db_error"
    return True, None


# Get All rooms
def get_rooms():
    cmd = "select id, room_no, room_type, price, created_at from rooms;"
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return False
    rooms = cursor.fetchall()

    cmd = "select r_id, check_in, check_out, status from reservations where r_id is not null;"
    cursor.execute(cmd)
    reservation_rows = cursor.fetchall() if cursor.rowcount else []

    statuses_by_room = {}
    for r_id, check_in, check_out, status in reservation_rows:
        state = reservation_status(check_in, check_out, status)
        statuses_by_room.setdefault(r_id, []).append(state)

    results = []
    for room in rooms:
        rid = room[0]
        computed = room_status_from_reservation_states(statuses_by_room.get(rid))
        results.append((room[0], room[1], room[2], room[3], room[4], computed))
    return results


# Get all reservations
def get_reservations():
    cmd = "select id, g_id, r_id, check_in, check_out, status from reservations;"
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return False
    rows = cursor.fetchall()
    results = []
    for row in rows:
        status_value = reservation_status(row[3], row[4], row[5])
        results.append((row[0], row[1], row[2], row[3], row[4], status_value))
    return results


# Add a reservation
def add_reservation(g_id, r_id, check_in="now", check_out=""):
    guest_id = normalize_prefixed_id(g_id, "guest_")
    room_id = normalize_prefixed_id(r_id, "room_")
    if not guest_id:
        return False, "guest_not_found"
    if not room_id:
        return False, "room_not_found"

    cursor.execute("select count(id) from guests where id = %s;", (guest_id,))
    if cursor.fetchone()[0] == 0:
        return False, "guest_not_found"

    cursor.execute("select room_type from rooms where id = %s;", (room_id,))
    room_row = cursor.fetchone()
    if not room_row:
        return False, "room_not_found"
    room_type = room_row[0]

    if not room_is_available(room_id):
        return False, "room_unavailable"

    reservation_id = _next_prefixed_id("reservations", "res_")

    check_in_value, check_in_err = parse_datetime_input(check_in, allow_empty=False)
    if check_in_err:
        return False, "invalid_check_in"

    check_out_value, check_out_err = parse_datetime_input(check_out, allow_empty=True)
    if check_out_err:
        return False, "invalid_check_out"

    if check_out_value and check_out_value < check_in_value:
        return False, "invalid_date_range"

    # r_type 作为“预订时房型快照”，避免房型变更导致历史记录语义不清
    cmd = "insert into reservations(id,g_id,check_in,check_out,r_id,r_type,status) values(%s,%s,%s,%s,%s,%s,%s);"
    try:
        cursor.execute(
            cmd,
            (reservation_id, guest_id, check_in_value, check_out_value, room_id, room_type, None),
        )
    except mysql.connector.IntegrityError:
        return False, "fk_error"
    if cursor.rowcount == 0:
        return False, "db_error"

    return True, None


# Get all room count
def get_total_rooms():
    cmd = "select count(room_no) from rooms;"
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return False
    return cursor.fetchone()[0]


# Check if a room is vacant
def booked():
    rooms = get_rooms()
    if not rooms:
        return 0
    return sum(1 for row in rooms if row[5] in ("使用中", "已预订"))


def vacant():
    return get_total_rooms() - booked()


def bookings():
    counts = bookings_by_type()
    return [counts.get("D", 0), counts.get("N", 0)]


def bookings_by_type():
    cursor.execute(
        """
        SELECT ros.room_type, COUNT(rs.id)
        FROM reservations rs
        JOIN rooms ros ON rs.r_id = ros.id
        GROUP BY ros.room_type;
        """
    )
    rows = cursor.fetchall() if cursor.rowcount else []
    return {str(room_type): int(count) for room_type, count in rows}


def report_reservation_details(check_in_from=None, check_in_to=None):
    """
    Join-based reservation details for reporting / future UI expansion.
    """
    cursor.execute(
        """
        SELECT
          rs.id        AS reservation_id,
          g.name       AS guest_name,
          ros.room_no  AS room_no,
          ros.room_type AS room_type,
          ros.price    AS price,
          rs.check_in  AS check_in,
          rs.check_out AS check_out,
          rs.status    AS status
        FROM reservations rs
        JOIN guests g   ON rs.g_id = g.id
        JOIN rooms  ros ON rs.r_id = ros.id
        WHERE (%s IS NULL OR rs.check_in >= %s)
          AND (%s IS NULL OR rs.check_in <= %s)
        ORDER BY rs.check_in DESC;
        """,
        (check_in_from, check_in_from, check_in_to, check_in_to),
    )
    return cursor.fetchall() if cursor.rowcount else []


def search_guests(keyword):
    kw = str(keyword).strip()
    if not kw:
        return get_guests() or []
    like = f"%{kw}%"
    cursor.execute(
        """
        SELECT id, name, address, email_id, phone, created_at
        FROM guests
        WHERE name LIKE %s OR email_id LIKE %s OR city LIKE %s
        ORDER BY created_at DESC;
        """,
        (like, like, like),
    )
    return cursor.fetchall() if cursor.rowcount else []


def room_status_summary():
    rooms = get_rooms() or []
    summary = {"可预订": 0, "已预订": 0, "使用中": 0}
    for row in rooms:
        status = row[5]
        if status in summary:
            summary[status] += 1
        else:
            summary[status] = summary.get(status, 0) + 1
    return summary


def list_available_rooms():
    rooms = get_rooms() or []
    return [row for row in rooms if len(row) > 5 and row[5] == "可预订"]


# Get total hotel value
def get_total_hotel_value():
    cmd = "select sum(price) from rooms;"
    cursor.execute(cmd)
    if cursor.rowcount == 0:
        return False
    value = cursor.fetchone()[0]

    return human_format(value)


def delete_reservation(id):
    reservation_id = normalize_prefixed_id(id, "res_") or str(id).strip()
    cursor.execute("delete from reservations where id=%s;", (reservation_id,))
    if cursor.rowcount == 0:
        return False
    return True


def delete_room(id):
    room_id = normalize_prefixed_id(id, "room_") or str(id).strip()
    cursor.execute("delete from rooms where id=%s;", (room_id,))
    if cursor.rowcount == 0:
        return False
    return True


def delete_guest(id):
    guest_id = normalize_prefixed_id(id, "guest_") or str(id).strip()
    cursor.execute("delete from guests where id=%s;", (guest_id,))
    if cursor.rowcount == 0:
        return False
    return True


def update_rooms(id, room_no, room_type, price):
    try:
        cursor.execute(
            "SELECT COUNT(id) FROM rooms WHERE room_no = %s AND id <> %s;",
            (room_no, id),
        )
        if cursor.fetchone()[0] > 0:
            return False, "duplicate_room_no"
    except mysql.connector.Error:
        pass

    room_id = normalize_prefixed_id(id, "room_") or str(id).strip()
    cmd = "update rooms set room_type = %s, price = %s, room_no = %s where id = %s;"
    try:
        cursor.execute(cmd, (room_type, price, room_no, room_id))
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            return False, "duplicate_room_no"
        return False, "db_error"
    if cursor.rowcount == 0:
        return False, "db_error"
    return True, None


def update_guests(name, address, id, phone):

    guest_id = normalize_prefixed_id(id, "guest_") or str(id).strip()
    cmd = "update guests set address = %s, phone = %s, name = %s where id = %s;"
    cursor.execute(cmd, (address, phone, name, guest_id))
    if cursor.rowcount == 0:
        return False
    return True


def update_reservations(
    g_id, check_in, room_id, reservation_date, check_out, type, id
):
    reservation_id = normalize_prefixed_id(id, "res_") or str(id).strip()
    guest_id = normalize_prefixed_id(g_id, "guest_") or str(g_id).strip()
    normalized_room_id = normalize_prefixed_id(room_id, "room_") or str(room_id).strip()

    if not reservation_id or not guest_id or not normalized_room_id:
        return False

    check_in_value, check_in_err = parse_datetime_input(check_in, allow_empty=False)
    if check_in_err:
        return False
    check_out_value, check_out_err = parse_datetime_input(check_out, allow_empty=True)
    if check_out_err:
        return False
    if check_out_value and check_out_value < check_in_value:
        return False

    r_date_value, r_date_err = parse_datetime_input(reservation_date, allow_empty=True)
    if r_date_err:
        return False

    cursor.execute(
        """
        UPDATE reservations
        SET check_in = %s,
            check_out = %s,
            g_id = %s,
            r_date = %s,
            r_type = %s,
            r_id = %s
        WHERE id = %s;
        """,
        (
            check_in_value,
            check_out_value,
            guest_id,
            r_date_value,
            type,
            normalized_room_id,
            reservation_id,
        ),
    )
    if cursor.rowcount == 0:
        return False
    return True


def active_guests():
    rows = get_reservations()
    if not rows:
        return 0
    count = sum(1 for row in rows if row[5] == "进行中")
    return count


def _sync_room_status(room_id):
    rid = normalize_prefixed_id(room_id, "room_") or str(room_id).strip()
    if not rid:
        return None

    cursor.execute(
        "select check_in, check_out, status from reservations where r_id = %s;",
        (rid,),
    )
    rows = cursor.fetchall() if cursor.rowcount else []
    states = [reservation_status(r[0], r[1], r[2]) for r in rows]
    return room_status_from_reservation_states(states)


def get_room_status(room_id):
    rid = normalize_prefixed_id(room_id, "room_") or str(room_id).strip()
    if not rid:
        return None
    return _sync_room_status(rid)


def room_is_available(room_id):
    return get_room_status(room_id) == "可预订"


def update_reservation(id, g_id, check_in, room_id, check_out):
    reservation_id = normalize_prefixed_id(id, "res_") or str(id).strip()
    guest_id = normalize_prefixed_id(g_id, "guest_") or str(g_id).strip()
    new_room_id = normalize_prefixed_id(room_id, "room_") or str(room_id).strip()

    if not reservation_id or not guest_id or not new_room_id:
        return False

    cursor.execute("SELECT r_id FROM reservations WHERE id = %s;", (reservation_id,))
    row = cursor.fetchone()
    if not row:
        return False
    old_room_id = row[0]

    cursor.execute("select count(id) from guests where id = %s;", (guest_id,))
    if cursor.fetchone()[0] == 0:
        return False

    cursor.execute("select room_type from rooms where id = %s;", (new_room_id,))
    room_row = cursor.fetchone()
    if not room_row:
        return False
    room_type = room_row[0]

    if old_room_id and str(old_room_id) != str(new_room_id):
        if not room_is_available(new_room_id):
            return False

    check_in_value, check_in_err = parse_datetime_input(check_in, allow_empty=False)
    if check_in_err:
        return False

    check_out_value, check_out_err = parse_datetime_input(check_out, allow_empty=True)
    if check_out_err:
        return False

    if check_out_value and check_out_value < check_in_value:
        return False

    # r_type 作为“预订时房型快照”
    cmd = "update reservations set check_in = %s, check_out = %s, g_id = %s, r_id = %s, r_type = %s where id = %s;"
    cursor.execute(
        cmd,
        (check_in_value, check_out_value, guest_id, new_room_id, room_type, reservation_id),
    )
    if cursor.rowcount == 0:
        return False
    return True


def update_reservation_status(id, status):
    reservation_id = normalize_prefixed_id(id, "res_") or str(id).strip()
    cmd = "update reservations set status = %s where id = %s;"
    cursor.execute(cmd, (status, reservation_id))
    if cursor.rowcount == 0:
        return False
    return True


def reservation_status(check_in, check_out, status):
    status_value = str(status).strip() if status is not None else ""
    status_lower = status_value.lower()
    if status_value in ("取消", "已取消") or status_lower in (
        "cancelled",
        "canceled",
        "cancel",
        "cancelled_reservation",
        "canceled_reservation",
    ):
        return "取消"

    now = datetime.now()
    if not check_in:
        return "已预订"

    if not check_out:
        return "已预订" if now < check_in else "进行中"

    if now < check_in:
        return "已预订"
    if now <= check_out:
        return "进行中"
    return "已结束"
