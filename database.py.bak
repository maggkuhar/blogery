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
    # База контактов (собранные разведчиком)
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

    # Задачи разведчика
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


def get_all_contacts(topic=None, platform=None, status=None, mailed=None):
    conn = get_db()
    q = "SELECT * FROM contacts WHERE 1=1"
    p = []
    if topic:
        q += " AND topic = ?"; p.append(topic)
    if platform:
        q += " AND source_platform = ?"; p.append(platform)
    if status:
        q += " AND status = ?"; p.append(status)
    if mailed is not None:
        q += " AND mailed = ?"; p.append(int(mailed))
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_scout_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM scout_tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_scout_task(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO scout_tasks (title, platforms, topics, regions, contact_types, keywords, entry_point, offer_rules, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("title"),
        ",".join(data.getlist("platforms")),
        ",".join(data.getlist("topics")),
        ",".join(data.getlist("regions")),
        ",".join(data.getlist("contact_types")),
        data.get("keywords", ""),
        data.get("entry_point", ""),
        data.get("offer_rules", ""),
        data.get("notes", ""),
    ))
    conn.commit()
    conn.close()


def delete_scout_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM scout_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_all_templates(format=None, subgroup=None):
    conn = get_db()
    query = "SELECT * FROM templates WHERE 1=1"
    params = []
    if format:
        query += " AND format = ?"
        params.append(format)
    if subgroup:
        query += " AND subgroup = ?"
        params.append(subgroup)
    query += " ORDER BY format, subgroup, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_template(template_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_template(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO templates (title, format, subgroup, content)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("title"),
        data.get("format"),
        data.get("subgroup"),
        data.get("content"),
    ))
    conn.commit()
    conn.close()


def update_template(template_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE templates SET title=?, format=?, subgroup=?, content=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        data.get("title"),
        data.get("format"),
        data.get("subgroup"),
        data.get("content"),
        template_id,
    ))
    conn.commit()
    conn.close()


def increment_template_usage(template_id):
    conn = get_db()
    conn.execute("UPDATE templates SET usage_count=usage_count+1 WHERE id=?", (template_id,))
    conn.commit()
    conn.close()


def delete_template(template_id):
    conn = get_db()
    conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()


def get_all_bots(platform=None, role=None, status=None):
    conn = get_db()
    query = "SELECT * FROM bots WHERE 1=1"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if role:
        query += " AND role = ?"
        params.append(role)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY platform, role, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bot(bot_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM bots WHERE id = ?", (bot_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_bot(data):
    conn = get_db()
    # Поддержка как ImmutableMultiDict (getlist), так и обычного dict
    def getlist(key):
        if hasattr(data, 'getlist'):
            return data.getlist(key)
        v = data.get(key)
        return v if isinstance(v, list) else ([v] if v else [])
    conn.execute("""
        INSERT INTO bots (name, platform, role, account, status,
            daily_limit, delay_min, delay_max, schedule, notes,
            target, topics, regions, contact_types, keywords, entry_point, offer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("role", "разведчик"),
        data.get("account"),
        data.get("status", "отключён"),
        data.get("daily_limit", 50),
        data.get("delay_min", 30),
        data.get("delay_max", 120),
        data.get("schedule", "09:00-22:00"),
        data.get("notes"),
        data.get("target"),
        ",".join(getlist("topics")),
        ",".join(getlist("regions")),
        ",".join(getlist("contact_types")),
        data.get("keywords"),
        data.get("entry_point"),
        data.get("offer"),
    ))
    conn.commit()
    conn.close()


def update_bot(bot_id, data):
    conn = get_db()
    def getlist(key):
        if hasattr(data, 'getlist'):
            return data.getlist(key)
        v = data.get(key)
        return v if isinstance(v, list) else ([v] if v else [])
    conn.execute("""
        UPDATE bots SET
            status=?,
            daily_limit=?, delay_min=?, delay_max=?, schedule=?, notes=?,
            target=?, topics=?, regions=?, contact_types=?, keywords=?, entry_point=?, offer=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        data.get("status"),
        data.get("daily_limit", 50),
        data.get("delay_min", 30),
        data.get("delay_max", 120),
        data.get("schedule", "09:00-22:00"),
        data.get("notes"),
        data.get("target"),
        ",".join(getlist("topics")),
        ",".join(getlist("regions")),
        ",".join(getlist("contact_types")),
        data.get("keywords"),
        data.get("entry_point"),
        data.get("offer"),
        bot_id,
    ))
    conn.commit()
    conn.close()


def toggle_bot_status(bot_id):
    conn = get_db()
    row = conn.execute("SELECT status FROM bots WHERE id = ?", (bot_id,)).fetchone()
    if row:
        new_status = "активен" if row["status"] == "отключён" else "отключён"
        conn.execute("UPDATE bots SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (new_status, bot_id))
        conn.commit()
    conn.close()


def bot_banned(bot_id, reason):
    conn = get_db()
    conn.execute("""
        UPDATE bots SET status='заблокирован', ban_count=ban_count+1, ban_reason=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (reason, bot_id))
    conn.commit()
    conn.close()


def delete_bot(bot_id):
    conn = get_db()
    conn.execute("DELETE FROM bots WHERE id = ?", (bot_id,))
    conn.commit()
    conn.close()


def get_all_groups(platform=None, status=None, folder=None, topic=None):
    conn = get_db()
    query = "SELECT * FROM groups WHERE 1=1"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if status:
        query += " AND status = ?"
        params.append(status)
    if folder:
        query += " AND folder = ?"
        params.append(folder)
    if topic:
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_group(group_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_group(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO groups (name, platform, url, members, topic, status, folder, comment, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("members", 0),
        data.get("topic"),
        data.get("status", "новый"),
        data.get("folder", "общие"),
        data.get("comment"),
        data.get("recommendation"),
    ))
    conn.commit()
    conn.close()


def update_group(group_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE groups SET
            name=?, platform=?, url=?, members=?, topic=?,
            status=?, folder=?, comment=?, recommendation=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("members", 0),
        data.get("topic"),
        data.get("status"),
        data.get("folder"),
        data.get("comment"),
        data.get("recommendation"),
        group_id,
    ))
    conn.commit()
    conn.close()


def delete_group(group_id):
    conn = get_db()
    conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()


def get_all_channels(platform=None, status=None, folder=None, topic=None):
    conn = get_db()
    query = "SELECT * FROM channels WHERE 1=1"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if status:
        query += " AND status = ?"
        params.append(status)
    if folder:
        query += " AND folder = ?"
        params.append(folder)
    if topic:
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_channel(channel_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_channel(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO channels (name, platform, url, subscribers, topic, status, folder, comment, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("subscribers", 0),
        data.get("topic"),
        data.get("status", "новый"),
        data.get("folder", "общие"),
        data.get("comment"),
        data.get("recommendation"),
    ))
    conn.commit()
    conn.close()


def update_channel(channel_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE channels SET
            name=?, platform=?, url=?, subscribers=?, topic=?,
            status=?, folder=?, comment=?, recommendation=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("subscribers", 0),
        data.get("topic"),
        data.get("status"),
        data.get("folder"),
        data.get("comment"),
        data.get("recommendation"),
        channel_id,
    ))
    conn.commit()
    conn.close()


def delete_channel(channel_id):
    conn = get_db()
    conn.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()


def get_all_bloggers(platform=None, status=None, folder=None, topic=None):
    conn = get_db()
    query = "SELECT * FROM bloggers WHERE 1=1"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if status:
        query += " AND status = ?"
        params.append(status)
    if folder:
        query += " AND folder = ?"
        params.append(folder)
    if topic:
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_blogger(blogger_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM bloggers WHERE id = ?", (blogger_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_blogger(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO bloggers (name, platform, url, subscribers, topic, status, folder, comment, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("subscribers", 0),
        data.get("topic"),
        data.get("status", "новый"),
        data.get("folder", "общие"),
        data.get("comment"),
        data.get("recommendation"),
    ))
    conn.commit()
    conn.close()


def update_blogger(blogger_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE bloggers SET
            name=?, platform=?, url=?, subscribers=?, topic=?,
            status=?, folder=?, comment=?, recommendation=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("subscribers", 0),
        data.get("topic"),
        data.get("status"),
        data.get("folder"),
        data.get("comment"),
        data.get("recommendation"),
        blogger_id,
    ))
    conn.commit()
    conn.close()


def delete_blogger(blogger_id):
    conn = get_db()
    conn.execute("DELETE FROM bloggers WHERE id = ?", (blogger_id,))
    conn.commit()
    conn.close()


# --- SMM аккаунты ---

def get_all_smm_accounts(platform=None, status=None):
    conn = get_db()
    query = "SELECT * FROM smm_accounts WHERE 1=1"
    params = []
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY platform, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_smm_account(account_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM smm_accounts WHERE id = ?", (account_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_smm_account(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO smm_accounts (name, platform, url, login, status, followers, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("login"),
        data.get("status", "активен"),
        data.get("followers", 0),
        data.get("notes"),
    ))
    conn.commit()
    conn.close()


def update_smm_account(account_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE smm_accounts SET name=?, platform=?, url=?, login=?, status=?, followers=?, notes=?,
        updated_at=CURRENT_TIMESTAMP WHERE id=?
    """, (
        data.get("name"),
        data.get("platform"),
        data.get("url"),
        data.get("login"),
        data.get("status"),
        data.get("followers", 0),
        data.get("notes"),
        account_id,
    ))
    conn.commit()
    conn.close()


def delete_smm_account(account_id):
    conn = get_db()
    conn.execute("DELETE FROM smm_accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()


# --- SMM посты ---

def get_all_smm_posts(status=None):
    conn = get_db()
    query = "SELECT * FROM smm_posts WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_smm_post(post_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM smm_posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_smm_post(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO smm_posts (title, content_text, media_path, platforms, account_ids, status, scheduled_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("title"),
        data.get("content_text"),
        data.get("media_path"),
        data.get("platforms"),
        data.get("account_ids"),
        data.get("status", "черновик"),
        data.get("scheduled_at"),
    ))
    conn.commit()
    conn.close()


def update_smm_post(post_id, data):
    conn = get_db()
    conn.execute("""
        UPDATE smm_posts SET title=?, content_text=?, media_path=?, platforms=?, account_ids=?,
        status=?, scheduled_at=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
    """, (
        data.get("title"),
        data.get("content_text"),
        data.get("media_path"),
        data.get("platforms"),
        data.get("account_ids"),
        data.get("status"),
        data.get("scheduled_at"),
        post_id,
    ))
    conn.commit()
    conn.close()


def delete_smm_post(post_id):
    conn = get_db()
    conn.execute("DELETE FROM smm_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
