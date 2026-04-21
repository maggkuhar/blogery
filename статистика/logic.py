from database import get_db


def get_stats():
    conn = get_db()

    def count(table, where="1=1", params=[]):
        return conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params).fetchone()[0]

    def count_by(table, field):
        rows = conn.execute(f"SELECT {field}, COUNT(*) as cnt FROM {table} GROUP BY {field}").fetchall()
        return {r[field]: r["cnt"] for r in rows}

    data = {
        "bloggers": {
            "total": count("bloggers"),
            "by_status": count_by("bloggers", "status"),
            "by_platform": count_by("bloggers", "platform"),
            "this_month": count("bloggers", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "groups": {
            "total": count("groups"),
            "by_status": count_by("groups", "status"),
            "by_platform": count_by("groups", "platform"),
            "this_month": count("groups", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "channels": {
            "total": count("channels"),
            "by_status": count_by("channels", "status"),
            "by_platform": count_by("channels", "platform"),
            "this_month": count("channels", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "bots": {
            "total": count("bots"),
            "active": count("bots", "status = 'активен'"),
            "banned": count("bots", "status = 'заблокирован'"),
        },
    }
    conn.close()
    return data
