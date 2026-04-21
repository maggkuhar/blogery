import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "blogery.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bloggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            url TEXT,
            subscribers INTEGER DEFAULT 0,
            topic TEXT,
            status TEXT DEFAULT 'новый',
            folder TEXT DEFAULT 'общие',
            comment TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            url TEXT,
            subscribers INTEGER DEFAULT 0,
            topic TEXT,
            status TEXT DEFAULT 'новый',
            folder TEXT DEFAULT 'общие',
            comment TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            url TEXT,
            members INTEGER DEFAULT 0,
            topic TEXT,
            status TEXT DEFAULT 'новый',
            folder TEXT DEFAULT 'общие',
            comment TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            role TEXT DEFAULT 'разведчик',
            account TEXT,
            status TEXT DEFAULT 'отключён',
            daily_limit INTEGER DEFAULT 50,
            delay_min INTEGER DEFAULT 30,
            delay_max INTEGER DEFAULT 120,
            schedule TEXT DEFAULT '09:00-22:00',
            ban_count INTEGER DEFAULT 0,
            ban_reason TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            format TEXT NOT NULL,
            subgroup TEXT NOT NULL,
            content TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS smm_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            url TEXT,
            login TEXT,
            status TEXT DEFAULT 'активен',
            followers INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS smm_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content_text TEXT,
            media_path TEXT,
            platforms TEXT,
            account_ids TEXT,
            status TEXT DEFAULT 'черновик',
            scheduled_at TEXT,
            published_at TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            phone TEXT,
            telegram TEXT,
            contact_url TEXT,
            name TEXT,
            source_url TEXT,
            source_platform TEXT,
            source_name TEXT,
            topic TEXT,
            region TEXT,
            description TEXT,
            audience_size INTEGER DEFAULT 0,
            audience_topic TEXT,
            entry_point TEXT,
            offer TEXT,
            template_id INTEGER,
            status TEXT DEFAULT 'новый',
            mailed INTEGER DEFAULT 0,
            mailed_at TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scout_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            platforms TEXT,
            topics TEXT,
            regions TEXT,
            contact_types TEXT,
            keywords TEXT,
            entry_point TEXT,
            offer_rules TEXT,
            status TEXT DEFAULT 'ожидает',
            found_count INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Миграция bots — добавить поля настроек
    for col, definition in [
        ('target', 'TEXT'), ('topics', 'TEXT'), ('regions', 'TEXT'),
        ('contact_types', 'TEXT'), ('keywords', 'TEXT'),
        ('entry_point', 'TEXT'), ('offer', 'TEXT'),
    ]:
        try:
            conn.execute(f'ALTER TABLE bots ADD COLUMN {col} {definition}')
        except Exception:
            pass

    # Миграция contacts — добавить новые колонки если БД старая
    for col, definition in [
        ('telegram', 'TEXT'), ('contact_url', 'TEXT'), ('description', 'TEXT'),
        ('audience_size', 'INTEGER DEFAULT 0'), ('audience_topic', 'TEXT'),
        ('entry_point', 'TEXT'), ('offer', 'TEXT'), ('template_id', 'INTEGER'),
    ]:
        try:
            conn.execute(f'ALTER TABLE contacts ADD COLUMN {col} {definition}')
        except Exception:
            pass

    # Миграция scout_tasks
    for col, definition in [('entry_point', 'TEXT'), ('offer_rules', 'TEXT')]:
        try:
            conn.execute(f'ALTER TABLE scout_tasks ADD COLUMN {col} {definition}')
        except Exception:
            pass

    conn.commit()
    conn.close()
