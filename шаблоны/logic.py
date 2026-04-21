from database import get_db


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
