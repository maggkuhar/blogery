from database import get_db


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
