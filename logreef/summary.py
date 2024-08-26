import datetime

from logreef.persistence import params
from logreef.persistence.database import Session


def get_for_all(
    db: Session, user_id: int, aquarium_name: str
) -> dict[str, dict[str, any]]:
    # get all param types with at least one value
    # get summaries per type
    summary = {}
    param_types = params.get_type_by_user(user_id, aquarium_name)
    for param_type in param_types:
        summary[param_type] = get_by_type(db, user_id, aquarium_name, param_type)
    return summary


def get_by_type(
    db: Session, user_id: int, aquarium_name: str, param_type: str
) -> dict[str, any]:
    # last two values
    # time since last two values in seconds
    # # data points in last week
    # # data points in last month
    # TODO add temporal weighted averages for week and month
    # keys: ["values", "timestamps", "time_since_secs", "n_last_week", "n_last_month"]

    summary = {
        "values": [],
        "ids": [],
        "timestamps": [],
        "time_since_secs": [],
        "count_last_week": None,
        "avg_last_week": None,
        "std_last_week": None,
    }

    # get last two info
    last_params = params.get_by_type(user_id, aquarium_name, param_type, limit=2)

    for param in last_params:
        summary["values"].append(float(param.value))
        summary["ids"].append(int(param.id))
        summary["timestamps"].append(param.timestamp)

    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    for ts in summary["timestamps"]:
        summary["time_since_secs"].append((now - ts).total_seconds())

    # get last week count
    results = params.get_stats_by_type_last_n_days(db, user_id, param_type, 7)

    summary["count_last_week"] = results["count"]
    summary["avg_last_week"] = results["avg"]
    summary["std_last_week"] = results["std"]

    return summary
