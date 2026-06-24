import csv
import os
from pathlib import Path

try:
    import mysql.connector
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: mysql-connector-python. Install it first with:\n"
        "  pip install mysql-connector-python"
    ) from exc


BASE_DIR = Path(__file__).resolve().parent / "FungiTastic-FewShot"
METADATA_DIR = BASE_DIR / "metadata"
IMAGE_DIR = Path(r"D:\Destop\images")

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "my-secret-pw")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fungitastic")
MYSQL_TABLE = os.getenv("MYSQL_TABLE", "fungitastic_dataset")


CSV_FILES = {
    "train": METADATA_DIR / "FungiTastic-FewShot-Train.csv",
    "val": METADATA_DIR / "FungiTastic-FewShot-Val.csv",
    "test": METADATA_DIR / "FungiTastic-FewShot-Test.csv",
}


def sql_ident(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def table_columns(headers: list[str]) -> list[str]:
    return ["id", "split", "image_path", *headers]


def create_table(cursor, headers: list[str]) -> None:
    columns_sql = [
        "`id` BIGINT AUTO_INCREMENT PRIMARY KEY",
        "`split` VARCHAR(16) NOT NULL",
        "`image_path` VARCHAR(512) NOT NULL",
    ]
    for header in headers:
        if header == "filename":
            columns_sql.append(f"{sql_ident(header)} VARCHAR(255) NOT NULL")
        elif header == "captions":
            columns_sql.append(f"{sql_ident(header)} LONGTEXT NULL")
        else:
            columns_sql.append(f"{sql_ident(header)} LONGTEXT NULL")

    unique_sql = "UNIQUE KEY `uq_split_filename` (`split`, `filename`)"
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {sql_ident(MYSQL_TABLE)} (
        {", ".join(columns_sql)},
        {unique_sql}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_sql)


def read_headers(csv_path: Path) -> list[str]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or []


def load_rows(csv_path: Path, split: str, target_headers: list[str]) -> list[tuple]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            filename = row.get("filename")
            if not filename:
                continue
            image_path = IMAGE_DIR / split / "500p" / filename
            values = [split, str(image_path)]
            for header in target_headers:
                value = row.get(header)
                if value == "":
                    value = None
                rows_value = value
                values.append(rows_value)
            rows.append(tuple(values))
    return rows


def main() -> None:
    if not MYSQL_PASSWORD and MYSQL_USER != "root":
        raise SystemExit("Set MYSQL_PASSWORD before running.")

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=False,
    )
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {sql_ident(MYSQL_DATABASE)} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE {sql_ident(MYSQL_DATABASE)}")

    all_headers: list[str] = []
    csv_headers: dict[str, list[str]] = {}
    all_rows: list[tuple] = []

    for split, csv_path in CSV_FILES.items():
        if not csv_path.exists():
            raise SystemExit(f"Missing CSV: {csv_path}")
        headers = read_headers(csv_path)
        csv_headers[split] = headers
        all_headers = list(dict.fromkeys([*all_headers, *headers]))

    create_table(cursor, all_headers)

    for split, csv_path in CSV_FILES.items():
        rows = load_rows(csv_path, split, all_headers)
        all_rows.extend(rows)

    cols = ["split", "image_path", *all_headers]
    placeholders = ", ".join(["%s"] * len(cols))
    col_sql = ", ".join(sql_ident(c) for c in cols)
    update_sql = ", ".join(
        f"{sql_ident(c)} = VALUES({sql_ident(c)})"
        for c in cols
        if c not in {"split", "filename"}
    )
    insert_sql = f"""
    INSERT INTO {sql_ident(MYSQL_TABLE)} ({col_sql})
    VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE {update_sql}
    """

    batch_size = 1000
    total = len(all_rows)
    for start in range(0, total, batch_size):
        batch = all_rows[start:start + batch_size]
        cursor.executemany(insert_sql, batch)
        conn.commit()
        print(f"Imported {min(start + batch_size, total)}/{total} rows")

    cursor.close()
    conn.close()
    print(f"Done. Database: {MYSQL_DATABASE}, table: {MYSQL_TABLE}")


if __name__ == "__main__":
    main()
