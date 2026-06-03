from sqlalchemy import inspect, text


def ensure_column(engine, table_name: str, column_name: str, definition: str) -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))


def run_lightweight_migrations(engine) -> None:
    ensure_column(engine, "keywords", "min_price", "INTEGER")
    ensure_column(engine, "keywords", "max_price", "INTEGER")
    ensure_column(engine, "keywords", "include_terms", "TEXT DEFAULT ''")
    ensure_column(engine, "keywords", "exclude_terms", "TEXT DEFAULT ''")
    ensure_column(engine, "keywords", "allowed_condition_ranks", "TEXT DEFAULT ''")
    ensure_column(engine, "products", "condition_rank", "VARCHAR(50)")
    ensure_column(engine, "notifications", "match_reason", "TEXT")
    ensure_column(engine, "notifications", "skip_reason", "TEXT")
