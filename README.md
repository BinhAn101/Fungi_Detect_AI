# FungiTastic-FewShot MySQL Import

This guide shows how to import the `FungiTastic-FewShot` dataset into a local MySQL Docker container.

## Data Layout

- Images: `FungiTastic-FewShot/images`
- Metadata:
  - `FungiTastic-FewShot/metadata/FungiTastic-FewShot-Train.csv`
  - `FungiTastic-FewShot/metadata/FungiTastic-FewShot-Val.csv`
  - `FungiTastic-FewShot/metadata/FungiTastic-FewShot-Test.csv`

Import script:

- `import_fungitastic_mysql.py`

## Storage Model

- 1 database: `fungitastic`
- 1 table: `fungitastic_dataset`
- add a `split` column to distinguish:
  - `train`
  - `val`
  - `test`
- keep images in the folder, store only paths and metadata in MySQL

## 4 Steps

### 0. Make sure MySQL image is ready
docker run --name some-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql


### 1. Check that Docker MySQL exposes the port

Run:

```cmd
docker ps
```

In the `PORTS` column, if you see:

```text
0.0.0.0:3306->3306/tcp
```

then MySQL is published to the host.

IF NOT:
docker run -d --name some-mysq -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=fungitastic -p 3306:3306 mysql

### 2. Install the Python driver

Run:

```cmd
pip install mysql-connector-python
```

If you are using a virtual environment:

```cmd
.venv\Scripts\pip.exe install mysql-connector-python
```

### 3. Set environment variables

Example in `cmd`:

```cmd
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=my-secret-pw
set MYSQL_DATABASE=fungitastic
```

Optional table name, only set this if you want a custom table name:

```cmd
set MYSQL_TABLE=fungitastic_dataset
```

Notes:
- `MYSQL_DATABASE=fungitastic` is used to auto-create the database on first run
- it is optional, but recommended for convenience
- `MYSQL_PASSWORD` must match the root password of your MySQL container

### 4. Run the import

Run:

```cmd
python import_fungitastic_mysql.py
```

If you want to use the Python inside `.venv`:

```cmd
.venv\Scripts\python.exe import_fungitastic_mysql.py
```

## What the script does

- creates the database if it does not exist
- creates the `fungitastic_dataset` table if it does not exist
- imports all 3 CSV files into the same table
- stores `split` so you can tell whether a row belongs to train, val, or test

## Query Examples

Get train rows:

```sql
SELECT * FROM fungitastic_dataset WHERE split = 'train';
```

Get validation rows:

```sql
SELECT * FROM fungitastic_dataset WHERE split = 'val';
```

Get test rows:

```sql
SELECT * FROM fungitastic_dataset WHERE split = 'test';
```

## Important Notes

- Do not let the model read the whole database and split later, because that can cause data leakage.
- During training:
  - train only reads `split='train'`
  - validation only reads `split='val'`
  - test only reads `split='test'`
- This dataset stores images in split folders, so the script maps paths like:
  - `FungiTastic-FewShot/images/train/500p`
  - `FungiTastic-FewShot/images/val/500p`
  - `FungiTastic-FewShot/images/test/500p`

## If the Database Does Not Exist Yet

You can also create it manually with SQL:

```sql
CREATE DATABASE fungitastic;
```

But the script will create it automatically when you run it.
