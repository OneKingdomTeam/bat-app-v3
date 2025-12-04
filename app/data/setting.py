from app.data.init import conn, curs
from app.model.setting import InstanceSetting
from app.exception.database import RecordNotFound


# Create settings table
curs.execute("""create table if not exists settings(
    setting_key text PRIMARY KEY,
    setting_value text
    )""")
conn.commit()


# -------------------------------
#   Helper Functions
# -------------------------------


def row_to_model(row: tuple) -> InstanceSetting:
    """Convert database row to InstanceSetting model."""
    setting_key, setting_value = row
    return InstanceSetting(
        setting_key=setting_key,
        setting_value=setting_value
    )


def model_to_dict(setting: InstanceSetting) -> dict:
    """Convert InstanceSetting model to dictionary."""
    return {
        "setting_key": setting.setting_key,
        "setting_value": setting.setting_value,
    }


# -------------------------------
#   CRUD Operations
# -------------------------------


def get_one(setting_key: str) -> InstanceSetting:
    """Get a single setting by key."""
    qry = "select * from settings where setting_key = :setting_key"
    params = {"setting_key": setting_key}

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        row = cursor.fetchone()
        if row:
            return row_to_model(row)
        else:
            raise RecordNotFound(msg=f"Setting '{setting_key}' was not found")
    finally:
        cursor.close()


def get_all() -> list[InstanceSetting]:
    """Get all settings."""
    qry = "select * from settings"

    cursor = conn.cursor()
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
        if rows:
            return [row_to_model(row) for row in rows]
        else:
            raise RecordNotFound(msg="No settings found")
    finally:
        cursor.close()


def create(setting: InstanceSetting) -> InstanceSetting:
    """Create a new setting."""
    qry = """
    insert into settings (setting_key, setting_value)
    values (:setting_key, :setting_value)
    """
    params = model_to_dict(setting)

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return setting
    finally:
        cursor.close()


def update(setting: InstanceSetting) -> InstanceSetting:
    """Update an existing setting."""
    qry = """
    update settings
    set setting_value = :setting_value
    where setting_key = :setting_key
    """
    params = model_to_dict(setting)

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        if cursor.rowcount == 0:
            raise RecordNotFound(msg=f"Setting '{setting.setting_key}' was not found")
        return setting
    finally:
        cursor.close()


def upsert(setting: InstanceSetting) -> InstanceSetting:
    """Insert or update a setting (upsert)."""
    qry = """
    insert into settings (setting_key, setting_value)
    values (:setting_key, :setting_value)
    on conflict(setting_key) do update set
        setting_value = excluded.setting_value
    """
    params = model_to_dict(setting)

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return setting
    finally:
        cursor.close()


def delete(setting_key: str) -> bool:
    """Delete a setting by key."""
    qry = "delete from settings where setting_key = :setting_key"
    params = {"setting_key": setting_key}

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        if cursor.rowcount == 0:
            raise RecordNotFound(msg=f"Setting '{setting_key}' was not found")
        return True
    finally:
        cursor.close()


def get_by_prefix(prefix: str) -> list[InstanceSetting]:
    """Get all settings with keys starting with a prefix (e.g., 'branding.')."""
    qry = "select * from settings where setting_key like :prefix"
    params = {"prefix": f"{prefix}%"}

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        rows = cursor.fetchall()
        if rows:
            return [row_to_model(row) for row in rows]
        else:
            return []
    finally:
        cursor.close()
