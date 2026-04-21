from database import get_db


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
