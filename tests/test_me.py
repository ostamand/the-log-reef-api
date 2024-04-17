from .helpers import save_random_user, get_random_string

from logreef.persistence import aquariums
from logreef.persistence.database import delete_from_db
from logreef.user import get_me


def test_me(test_db):
    user = save_random_user(test_db)
    assert user

    n_aquariums = 5
    aquarium_names = []
    for _ in range(n_aquariums):
        aquarium_names.append(get_random_string(10))
        aquariums.create(test_db, user.id, aquarium_names[-1])

    me = get_me(test_db, user.id)
    assert me
    assert me.username == user.username
    assert me.aquariums
    assert len(me.aquariums) == n_aquariums

    delete_from_db(test_db, user)

    all_aquariums = aquariums.get_all(test_db, user.id)
    for aquarium in all_aquariums:
        delete_from_db(test_db, aquarium)

    all_aquariums = aquariums.get_all(test_db, user.id)
    assert len(all_aquariums) == 0
