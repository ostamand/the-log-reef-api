from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import text

from logreef.persistence import models
from logreef.persistence import aquariums
from logreef.config import (
    TestKits,
    ParamTypes,
    default_test_kits,
    get_param_type,
    get_test_kit,
)
from logreef.units.converter import convert_unit_for
from logreef import schemas


def get_type_by_user(db: Session, user_id: int, aquarium_name: str) -> list[str]:
    sql = text(
        """
            SELECT DISTINCT(param_types.name)
            FROM param_values
            JOIN users ON param_values.user_id = users.id
            JOIN param_types ON param_values.param_type_name = param_types.name
            JOIN aquariums ON param_values.aquarium_id = aquariums.id
            WHERE param_values.user_id = :user_id
                AND aquariums.name = :aquarium_name
            """
    )
    result = db.execute(sql, {"user_id": user_id, "aquarium_name": aquarium_name})
    return [row[0] for row in result]


def get_type(db: Session, name: str):
    return (
        db.query(models.ParamType)
        .filter(models.ParamType.name == name.strip().lower())
        .first()
    )


def create(
    db: Session,
    user_id: int,
    aquarium: models.Aquarium | str | int,
    param_type: models.ParamType | str | ParamTypes,
    value: float,
    timestamp: datetime | None = None,
    test_kit: models.TestKit | str | TestKits | None = None,
    note: str | None = None,
    commit: bool = True,
    convert_value: bool = True,
):
    now = datetime.now(timezone.utc)

    timestamp = now if not timestamp else timestamp

    if type(param_type) is models.ParamType:
        param_type = get_param_type(param_type.name)
    elif type(param_type) is str:
        param_type = get_param_type(param_type)

    if type(aquarium) is str:
        aquarium_id = aquariums.get_by_name(db, user_id, aquarium).id
    elif type(aquarium) is int:
        aquarium_id = aquarium
    elif type(aquarium) is models.Aquarium:
        aquarium_id = aquarium.id

    if type(test_kit) is str:
        test_kit = get_test_kit(test_kit)
    elif type(test_kit) is models.TestKit:
        test_kit = get_test_kit(test_kit.name)
    elif test_kit is None:
        test_kit = default_test_kits[param_type.value]

    # convert value
    # TODO: Also save value not converted?
    if convert_value:
        value_converted = convert_unit_for(param_type, test_kit, value)
        if value_converted is None:
            raise Exception(f"{param_type.value} and/or {test_kit.value} not supported")
    else:
        value_converted = value

    # TODO check if user is owner of aquarium?
    db_value = models.ParamValue(
        user_id=user_id,
        param_type_name=param_type.value,
        aquarium_id=aquarium_id,
        test_kit_name=test_kit.value,
        value=value_converted,
        timestamp=timestamp,
        created_on=now,
        updated_on=now,
        note=note,
    )

    if commit:
        db.add(db_value)
        db.commit()
        db.refresh(db_value)

    return db_value


def get_stats_by_type_last_n_days(
    db: Session, user_id: int, param_type: str, n_days: int
):
    sql = text(
        """
        SELECT COUNT(1) as count, AVG(value) as avg, STDDEV(value) as std
        FROM param_values
        WHERE user_id = :user_id
        AND param_type_name = :param_type
        AND param_values.timestamp > NOW()::DATE - :n_days;    
        """
    )
    cols = ["count", "avg", "std"]
    result = db.execute(
        sql, {"param_type": param_type, "user_id": user_id, "n_days": n_days}
    )
    data = [row for row in result]
    if len(data) > 0:
        return {
            key: float(value) if value is not None else value
            for key, value in zip(cols, data[0])
        }
    return {}


def get_by_type(
    db: Session,
    user_id: int,
    aquarium: str,
    param_type: str | ParamTypes = None,
    days: int | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[schemas.ParamInfo]:
    cols = schemas.ParamInfo.get_fields()
    query = """
    SELECT 
        p.id, 
        p.param_type_name, 
        param_types.display_name AS param_type_display_name, 
        p.test_kit_name, 
        t.display_name AS test_kit_display_name, 
        p.value,
        param_types.unit, 
        p.timestamp, 
        p.note,
        p.created_on,
        p.updated_on
    FROM param_values AS p
    LEFT JOIN test_kits AS t ON p.test_kit_name = t.name
    LEFT JOIN param_types ON p.param_type_name = param_types.name
    LEFT JOIN aquariums ON p.aquarium_id =aquariums.id
    WHERE p.user_id = :user_id
        AND aquariums.name = :aquarium_name
    """
    if param_type is not None:
        if type(param_type) is ParamTypes:
            param_type = param_type.value
        query += " AND p.param_type_name = :param_type_name"

    data = {
        "param_type_name": param_type,
        "user_id": user_id,
        "aquarium_name": aquarium,
    }
    if days is not None:
        query += " AND p.timestamp > current_date - interval ':days' day"
        data["days"] = days

    query += " ORDER BY p.timestamp DESC"

    if limit is not None:
        query += " LIMIT :limit"
        data["limit"] = limit
    if offset is not None:
        query += " OFFSET :offset"
        data["offset"] = offset

    sql = text(query)
    result = db.execute(sql, data)
    out = []
    for row in result:
        out.append(schemas.ParamInfo(**{cols[i]: item for i, item in enumerate(row)}))
    return out


def get_count_by_type(
    db: Session,
    user_id: int,
    aquarium: str,
    param_type: str | ParamTypes = None,
    days: int | None = None,
):
    query = """
    SELECT COUNT(p.id)
    FROM param_values AS p
    LEFT JOIN test_kits AS t ON p.test_kit_name = t.name
    LEFT JOIN param_types ON p.param_type_name = param_types.name
    LEFT JOIN aquariums ON p.aquarium_id =aquariums.id
    WHERE p.user_id = :user_id
        AND aquariums.name = :aquarium_name
    """
    if param_type is not None:
        if type(param_type) is ParamTypes:
            param_type = param_type.value
        query += " AND p.param_type_name = :param_type_name"

    data = {
        "param_type_name": param_type,
        "user_id": user_id,
        "aquarium_name": aquarium,
    }
    if days is not None:
        query += " AND p.timestamp > current_date - interval ':days' day"
        data["days"] = days
    sql = text(query)
    result = db.execute(sql, data)
    data = [row for row in result]
    return {"count": data[0][0]}


def get_param_by_id(db: Session, user_id: int, param_id: int) -> schemas.ParamInfo:
    cols = schemas.ParamInfo.get_fields()
    sql = text(
        """
        SELECT 
            v.id, 
            v.param_type_name, 
            param_types.display_name AS param_type_display_name,
            t.name AS test_kit_name, 
            t.display_name AS test_kit_display_name, 
            v.value, 
            param_types.unit AS unit,
            v.timestamp, 
            v.note,
            v.created_on,
            v.updated_on
        FROM param_values AS v
        LEFT JOIN test_kits AS t ON v.test_kit_name = t.name 
        LEFT JOIN param_types ON v.param_type_name = param_types.name
        WHERE user_id = :user_id and id = :param_id
        LIMIT 1;
        """
    )
    result = db.execute(sql, {"param_id": param_id, "user_id": user_id})
    data = [row for row in result]
    if len(data) == 1:
        return schemas.ParamInfo(**{cols[i]: item for i, item in enumerate(data[0])})
    return schemas.ParamInfo()


def delete_by_id(db: Session, user_id: int, param_id: int):
    rows = (
        db.query(models.ParamValue)
        .filter(models.ParamValue.user_id == user_id)
        .filter(models.ParamValue.id == param_id)
        .delete()
    )
    db.commit()
    return rows


def update_by_id(
    db: Session,
    user_id: int,
    param_id: int,
    value: float | None = None,
    note: str | None = None,
):
    updates = {models.ParamValue.updated_on: datetime.now(timezone.utc)}
    if value is not None:
        updates[models.ParamValue.value] = value
    if note is not None:
        updates[models.ParamValue.note] = note

    db.query(models.ParamValue).filter(models.ParamValue.user_id == user_id).filter(
        models.ParamValue.id == param_id
    ).update(updates)
    db.commit()
    return (
        db.query(models.ParamValue)
        .filter(models.ParamValue.user_id == user_id)
        .filter(models.ParamValue.id == param_id)
        .first()
    )
