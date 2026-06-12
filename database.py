import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# ======================
# LOAD ENV
# ======================
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite")


# ======================
# CONNECTION
# ======================
def get_connection():
    if DB_TYPE == "postgres":
        import psycopg2
        from psycopg2.extras import RealDictCursor

        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor,
        )

    conn = sqlite3.connect("triage.db")
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# QUERY ADAPTER
# ======================
def adapt_query(query):
    if DB_TYPE == "postgres":
        return query.replace("?", "%s")
    return query


# ======================
# EXECUTE HELPER
# ======================
def execute(query, params=None, fetch=False):
    conn = get_connection()
    cur = conn.cursor()

    query = adapt_query(query)

    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)

    result = cur.fetchall() if fetch else None

    conn.commit()
    cur.close()
    conn.close()

    return result


# ======================
# INIT TRIAGE TABLE
# ======================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    if DB_TYPE == "postgres":
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS triage_records(
            id SERIAL PRIMARY KEY,

            user_id TEXT NOT NULL,
            organization TEXT,

            nama_pasien TEXT,
            umur TEXT,
            petugas TEXT,

            keluhan TEXT,
            anamnesa TEXT,

            vital TEXT,
            abcde TEXT,

            triage_result TEXT,
            masalah TEXT,
            plan TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user_email
            FOREIGN KEY (user_id)
            REFERENCES users(email)
            ON DELETE CASCADE
        )
        """
        )
    else:
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS triage_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT,
            organization TEXT,

            nama_pasien TEXT,
            umur TEXT,
            petugas TEXT,

            keluhan TEXT,
            anamnesa TEXT,

            vital TEXT,
            abcde TEXT,

            triage_result TEXT,
            masalah TEXT,
            plan TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

    conn.commit()
    conn.close()


# ======================
# USER TABLE
# ======================
def init_user_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT,
        active INTEGER,
        expired_at TEXT,
        role TEXT,

        must_change_password INTEGER DEFAULT 0,
         
        organization TEXT,
        alamat TEXT,
        pimpinan TEXT,
        no_wa TEXT
    )
    """
    )

    conn.commit()
    conn.close()


def create_user(
    email,
    password,
    role="user",
    organization=None,
    alamat=None,
    pimpinan=None,
    no_wa=None,
):
    activate_value = 1 if role == "admin" else 0

    if DB_TYPE == "postgres":
        execute(
            """
        INSERT INTO users (email, password, active, expired_at, role, organization, alamat, pimpinan, no_wa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (email)
        DO UPDATE SET
            password = EXCLUDED.password,
            active = EXCLUDED.active,
            expired_at = EXCLUDED.expired_at,
            role = EXCLUDED.role,
            organization = EXCLUDED.organization,
            alamat = EXCLUDED.alamat,
            pimpinan = EXCLUDED.pimpinan,
            no_wa = EXCLUDED.no_wa
        """,
            (email, password, 0, None, role, organization, alamat, pimpinan, no_wa),
        )

    else:
        execute(
            """
        INSERT OR REPLACE INTO users
        (email, password, active, expired_at, role, organization, alamat, pimpinan, no_wa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (email, password, 0, None, role, organization, alamat, pimpinan, no_wa),
        )

    return True


def get_user(email):
    rows = execute("SELECT * FROM users WHERE email=?", (email,), fetch=True)

    if not rows or len(rows) == 0:
        return None

    row = rows[0]

    base_data = {
        "email": row["email"],
        "password": row["password"],
        "active": row.get("active"),
        "expired_at": row.get("expired_at"),
        "role": row["role"],
        "must_change_password": row.get("must_change_password"),
        "organization": row["organization"],
        "alamat": row["alamat"],
        "pimpinan": row["pimpinan"],
        "no_wa": row["no_wa"],
    }

    if row["role"] == "admin":
        base_data["active"] = 1
        base_data["expired_at"] = None

    return base_data


def activate_user(email, days=30):
    rows = execute("SELECT expired_at FROM users WHERE email=?", (email,), fetch=True)

    now = datetime.now().timestamp()

    if rows and rows[0]["expired_at"]:
        current_exp = float(rows[0]["expired_at"])
        base = max(current_exp, now)
    else:
        base = now

    new_expired = base + (days * 86400)

    execute(
        """
    UPDATE users
    SET active=1, expired_at=?
    WHERE email=?
    """,
        (new_expired, email),
    )


# ======================
# SAVE TRIAGE
# ======================
def save_triage(patient, triage_result, plan_text, user_id):
    if not user_id:
        raise ValueError("User ID is wajib ada (tidak boleh kosong)")

    anamnesa_full = f"""
{patient.get("resume_anamnesa","")}

{patient.get("anamnesa_detail","")}
"""

    execute(
        """
    INSERT INTO triage_records (
        user_id,
        organization,
        nama_pasien,
        umur,
        petugas,
        keluhan,
        anamnesa,
        vital,
        abcde,
        triage_result,
        masalah,
        plan
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            user_id,
            "default",
            patient.get("nama"),
            patient.get("umur"),
            patient.get("petugas"),
            patient.get("keluhan"),
            anamnesa_full,
            json.dumps(patient.get("vital", {})),
            json.dumps(patient.get("abcde", {})),
            triage_result.get("triage"),
            json.dumps(triage_result.get("problems", [])),
            plan_text,
        ),
    )


# ======================
# DASHBOARD COUNTS
# ======================
def get_triage_counts(user_id):

    rows = execute(
        """
        SELECT 
            SUM(CASE WHEN LOWER(triage_result) LIKE 'green' THEN 1 ELSE 0 END) as hijau,
            SUM(CASE WHEN LOWER(triage_result) LIKE 'yellow' THEN 1 ELSE 0 END) as kuning,
            SUM(CASE WHEN LOWER(triage_result) LIKE 'red' THEN 1 ELSE 0 END) as merah
        FROM triage_records
        WHERE user_id=?
    """,
        (user_id,),
        fetch=True,
    )

    if not rows:
        return 0, 0, 0

    r = rows[0]

    return (
        r.get("hijau", 0) or 0,
        r.get("kuning", 0) or 0,
        r.get("merah", 0) or 0,
    )


# ======================
# HISTORY
# ======================
def get_all_triage(user_id):
    rows = execute(
        """
        SELECT * FROM triage_records
        WHERE user_id=?
        ORDER BY created_at DESC
    """,
        (user_id,),
        fetch=True,
    )

    result = []
    for r in rows:
        item = dict(r)
        try:
            item["masalah"] = json.loads(item["masalah"] or "[]")
        except:
            item["masalah"] = []
        result.append(item)
    return result


# ======================
# ADMIN DASHBOARD
# ======================
def get_all_users_triage_counts():
    rows = execute(
        """
        SELECT 
            user_id,
            SUM(CASE WHEN triage_result LIKE '%GREEN%' THEN 1 ELSE 0 END) as hijau,
            SUM(CASE WHEN triage_result LIKE '%YELLOW%' THEN 1 ELSE 0 END) as kuning,
            SUM(CASE WHEN triage_result LIKE '%RED%' THEN 1 ELSE 0 END) as merah
        FROM triage_records
        GROUP BY user_id
    """,
        fetch=True,
    )

    result = []
    for r in rows:
        result.append(
            {
                "user_id": r["user_id"],
                "hijau": r["hijau"] or 0,
                "kuning": r["kuning"] or 0,
                "merah": r["merah"] or 0,
            }
        )

    return result


# ======================
# ADMIN FUNCTIONS
# ======================
def get_all_users():
    rows = execute(
        """
        SELECT email, active, expired_at, role,
                organization, alamat, pimpinan, no_wa
        FROM users
        ORDER BY email
    """,
        fetch=True,
    )

    return [
        {
            "email": row["email"],
            "active": row["active"],
            "expired_at": row["expired_at"],
            "role": row["role"],
            "organization": row["organization"],
            "alamat": row["alamat"],
            "pimpinan": row["pimpinan"],
            "no_wa": row["no_wa"],
        }
        for row in rows
    ]


def delete_user(email):
    execute("DELETE FROM users WHERE email=?", (email,))


def deactivate_user(email):
    execute(
        """
        UPDATE users
        SET active=0
        WHERE email=?
    """,
        (email,),
    )


def reset_password(email, new_password="123456"):
    execute(
        """
        UPDATE users
        SET password=?,
            must_change_password=1
        WHERE email=?
    """,
        (new_password, email),
    )
