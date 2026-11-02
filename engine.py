import sqlite3
from contextlib import closing
from pathlib import Path


def authorize(action, arg1, arg2, database, trigger):
    denied = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA,
              sqlite3.SQLITE_CREATE_VTABLE, sqlite3.SQLITE_DROP_VTABLE}
    return sqlite3.SQLITE_DENY if action in denied else sqlite3.SQLITE_OK


def snapshot(db, checks):
    result = {}
    for name, query in checks.items():
        if not query.lstrip().upper().startswith("SELECT "):
            raise ValueError("invariants must be SELECT queries")
        rows = db.execute(query).fetchmany(2)
        if len(rows) != 1 or len(rows[0]) != 1:
            raise ValueError("expected one scalar for each invariant")
        result[name] = rows[0][0]
    return result


def evaluate(data):
    if not data["checks"] or ("source" in data) == ("fixture_sql" in data):
        raise ValueError("supply one source and at least one invariant")
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("PRAGMA foreign_keys=ON")
        if "source" in data:
            uri = Path(data["source"]).resolve().as_uri() + "?mode=ro"
            with closing(sqlite3.connect(uri, uri=True)) as source:
                source.backup(db)
        db.set_authorizer(authorize)
        try:
            if "fixture_sql" in data:
                db.executescript(data["fixture_sql"])
            before = snapshot(db, data["checks"])
            db.executescript(data["migration_sql"])
            after = snapshot(db, data["checks"])
            db.set_authorizer(None)
            foreign_errors = len(db.execute("PRAGMA foreign_key_check").fetchall())
            differences = {k: [v, after[k]] for k,v in before.items() if v != after[k]}
            return {"passed": not differences and not foreign_errors, "differences": differences,
                    "foreign_key_errors": foreign_errors, "after": after}
        except sqlite3.DatabaseError as error:
            return {"passed": False, "sql_error": str(error)}
