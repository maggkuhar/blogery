from database import get_db


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
