# Migration Rehearsal

Try a SQLite migration on an in-memory copy of a schema fixture or existing database. Compare named business invariants before and after and reject integrity regressions.

## Run locally

Use Python 3.12. The project uses the standard library. From the repository root:

```sh
python cli.py example.json
python -m unittest -v
```

The included example is synthetic. Pass a different UTF-8 JSON file to inspect your own input. The command prints JSON to stdout. Invalid input returns status 2 and an explanation on stderr. See [CONTRACT.md](CONTRACT.md) for input fields and interpretation.

## Operational limits

SQLite only. An in-memory copy must fit in RAM. ATTACH, DETACH, PRAGMA, extension loading and virtual-table creation are denied in user SQL. This tool is for trusted migrations, not adversarial SQL isolation. Verify business invariants beyond row counts.

## Resumen en español

Ensaya una migración en memoria, verifica invariantes SQL y registra las diferencias sin modificar la base de origen.
