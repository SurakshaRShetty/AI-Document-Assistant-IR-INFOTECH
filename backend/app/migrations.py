from sqlalchemy import text

# Idempotent, additive-only migrations for columns introduced after the
# original tables were created. Safe to run on every startup.
MIGRATIONS = [
    "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS page_number INTEGER",
    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS sources TEXT",
]


def run_migrations(engine):
    with engine.begin() as conn:
        for statement in MIGRATIONS:
            conn.execute(text(statement))
