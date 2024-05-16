from .helpers import get_random_string, save_random_user_and_aquarium

from logreef.persistence import events
from logreef.persistence.database import delete_from_db


def test_can_create_new_water_change(test_db):
    test_description = get_random_string(10)
    user, aquarium = save_random_user_and_aquarium(test_db)
    event = events.create_water_change(
        test_db,
        user.id,
        aquarium.id,
        quantity=20,
        unit_name="gal",
        description=test_description,
    )
    assert event.id is not None
    assert event.water_change_id is not None
    assert event.dosing is None
    assert event.water_change is not None
    assert event.water_change.unit_name == "gal"
    assert event.water_change.description == test_description

    events_in_db = events.get_water_changes(
        test_db,
        user.id,
        aquarium.id,
    )
    assert len(events_in_db) == 1
    assert events_in_db[0].user_id == user.id
    assert events_in_db[0].water_change.description == test_description

    delete_from_db(
        test_db, event.water_change
    )  # not sure why cascade not working from user
    delete_from_db(test_db, user)
