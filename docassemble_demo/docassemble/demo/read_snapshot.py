from docassemble.base.util import variables_snapshot_connection, user_info

__all__ = ['analyze']


def analyze():
    conn = variables_snapshot_connection()
    cur = conn.cursor()
    cur.execute("select data->>'favorite_fruit' from jsonstorage where filename='" + user_info().filename + "'")
    counts = {}
    for record in cur.fetchall():
        fruit = record[0].lower()
        if fruit not in counts:
            counts[fruit] = 0
        counts[fruit] += 1
    conn.close()
    return counts
