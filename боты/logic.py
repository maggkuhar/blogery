from database import get_db


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
