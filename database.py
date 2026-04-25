# database.py
import sqlite3
from datetime import datetime

DB_PATH = "students.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # better concurrent read performance
    return conn


def create_database():
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # ── CORE LOOKUP TABLES ────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS difficulty_levels (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT    NOT NULL UNIQUE,
            rank  INTEGER NOT NULL UNIQUE   -- 1=Easy, 2=Medium, 3=Hard
        )""")

        # Seed difficulty levels if not already present
        cursor.executemany("""
            INSERT OR IGNORE INTO difficulty_levels (label, rank) VALUES (?, ?)
        """, [("Easy", 1), ("Medium", 2), ("Hard", 3)])

        # ── USERS ─────────────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_logins (
            student_name TEXT PRIMARY KEY,
            password     TEXT NOT NULL,
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS allowed_students (
            student_name TEXT PRIMARY KEY
                REFERENCES student_logins(student_name)
                ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            student_name TEXT NOT NULL
                REFERENCES allowed_students(student_name)
                ON DELETE CASCADE,
            subject_id   INTEGER NOT NULL
                REFERENCES subjects(id)
                ON DELETE CASCADE,
            enrolled_at  TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (student_name, subject_id)
        )""")

        # ── QUESTION BANK ─────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_bank (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id     INTEGER NOT NULL
                REFERENCES subjects(id) ON DELETE CASCADE,
            difficulty_id  INTEGER NOT NULL
                REFERENCES difficulty_levels(id),
            question       TEXT    NOT NULL,
            choice_a       TEXT    NOT NULL,
            choice_b       TEXT    NOT NULL,
            choice_c       TEXT    NOT NULL,
            choice_d       TEXT    NOT NULL,
            correct_letter TEXT    NOT NULL CHECK(correct_letter IN ('A','B','C','D')),
            uploaded_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE(subject_id, question)   -- prevent duplicate questions per subject
        )""")

        # ── PERFORMANCE ───────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT    NOT NULL
                REFERENCES student_logins(student_name) ON DELETE CASCADE,
            subject_id   INTEGER NOT NULL
                REFERENCES subjects(id) ON DELETE CASCADE,
            difficulty_id INTEGER NOT NULL
                REFERENCES difficulty_levels(id),
            score        INTEGER NOT NULL CHECK(score BETWEEN 0 AND 5),
            submitted_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )""")

        # ── STUDY MATERIAL ────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_material (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id  INTEGER NOT NULL
                REFERENCES subjects(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            content     TEXT,
            file_name   TEXT,
            file_data   BLOB,
            uploaded_at TEXT    NOT NULL DEFAULT (datetime('now')),
            CHECK (content IS NOT NULL OR file_data IS NOT NULL)
        )""")

        # ── CHAT HISTORY ──────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT    NOT NULL
                REFERENCES student_logins(student_name) ON DELETE CASCADE,
            subject_id   INTEGER NOT NULL
                REFERENCES subjects(id) ON DELETE CASCADE,
            role         TEXT    NOT NULL CHECK(role IN ('user','assistant')),
            content      TEXT    NOT NULL,
            sent_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )""")

        # ── AUDIT LOG ─────────────────────────────────────────────────────────

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            actor     TEXT NOT NULL,
            role      TEXT NOT NULL CHECK(role IN ('teacher','student','system')),
            action    TEXT NOT NULL,
            detail    TEXT,
            logged_at TEXT NOT NULL DEFAULT (datetime('now'))
        )""")

        # ── INDEXES ───────────────────────────────────────────────────────────

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_student    ON performance(student_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_subject    ON performance(subject_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_submitted  ON performance(submitted_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_qbank_subject   ON question_bank(subject_id, difficulty_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_student    ON chat_history(student_name, subject_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_actor     ON audit_log(actor)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_material_subj   ON study_material(subject_id)")

        # ── VIEWS ─────────────────────────────────────────────────────────────

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_student_performance_summary AS
        SELECT
            p.student_name,
            s.name                        AS subject,
            d.label                       AS difficulty,
            COUNT(*)                      AS attempts,
            ROUND(AVG(p.score) * 20, 1)   AS avg_percent,
            MAX(p.score)                  AS best_score,
            MIN(p.score)                  AS worst_score,
            MAX(p.submitted_at)           AS last_attempt
        FROM performance p
        JOIN subjects          s ON p.subject_id    = s.id
        JOIN difficulty_levels d ON p.difficulty_id = d.id
        GROUP BY p.student_name, s.name, d.label
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_class_scoreboard AS
        SELECT
            p.student_name,
            s.name                      AS subject,
            d.label                     AS difficulty,
            COUNT(*)                    AS attempts,
            ROUND(AVG(p.score)*20, 1)   AS avg_percent,
            MAX(p.score)                AS best_score
        FROM performance p
        JOIN subjects          s ON p.subject_id    = s.id
        JOIN difficulty_levels d ON p.difficulty_id = d.id
        GROUP BY p.student_name, s.name, d.label
        ORDER BY avg_percent DESC
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_question_counts AS
        SELECT
            s.name    AS subject,
            d.label   AS difficulty,
            d.rank    AS difficulty_rank,
            COUNT(*)  AS total_questions
        FROM question_bank q
        JOIN subjects          s ON q.subject_id    = s.id
        JOIN difficulty_levels d ON q.difficulty_id = d.id
        GROUP BY s.name, d.label
        ORDER BY s.name, d.rank
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_struggling_students AS
        SELECT
            p.student_name,
            s.name                    AS subject,
            ROUND(AVG(p.score)*20,1)  AS avg_percent,
            COUNT(*)                  AS total_attempts
        FROM performance p
        JOIN subjects s ON p.subject_id = s.id
        GROUP BY p.student_name, s.name
        HAVING avg_percent < 50
        ORDER BY avg_percent ASC
        """)

        conn.execute("COMMIT")
        print(f"[{datetime.now().isoformat()}] Database initialized successfully.")

    except Exception as e:
        conn.execute("ROLLBACK")
        print(f"[{datetime.now().isoformat()}] Database init FAILED — rolled back. Error: {e}")
        raise
    finally:
        conn.close()


# ── HELPER: resolve or create a subject by name ───────────────────────────────
def get_or_create_subject(conn, name: str) -> int:
    """Returns the subject id, inserting if it doesn't exist."""
    conn.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (name,))
    row = conn.execute("SELECT id FROM subjects WHERE name = ?", (name,)).fetchone()
    return row[0]


# ── HELPER: resolve difficulty id by label ────────────────────────────────────
def get_difficulty_id(conn, label: str) -> int:
    row = conn.execute(
        "SELECT id FROM difficulty_levels WHERE label = ?", (label.strip().capitalize(),)
    ).fetchone()
    if not row:
        raise ValueError(f"Unknown difficulty: {label}")
    return row[0]


# ── HELPER: audit logger ──────────────────────────────────────────────────────
def log_audit(conn, actor: str, role: str, action: str, detail: str = None):
    conn.execute(
        "INSERT INTO audit_log (actor, role, action, detail, logged_at) VALUES (?,?,?,?,?)",
        (actor, role, action, detail, datetime.now().isoformat())
    )


if __name__ == "__main__":
    create_database()
