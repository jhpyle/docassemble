from docassemble.base.util import variables_snapshot_connect, user_info

__all__ = ['analyze']


def analyze():
    with variables_snapshot_connect() as conn:
        with conn.connection.cursor() as cur:
            cur.execute("select data->>'favorite_fruit' from jsonstorage where filename='" + user_info().filename + "'")
            counts = {}
            for record in cur.fetchall():
                fruit = record[0].lower()
                if fruit not in counts:
                    counts[fruit] = 0
                counts[fruit] += 1
    return counts
