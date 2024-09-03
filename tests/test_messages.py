from logreef.persistence import messages
from logreef.persistence.database import delete_from_db


def test_can_save_message(test_db):
    test_email = "demo@thelogreef.com"
    test_source = "thelogreef"
    test_message = "message"
    message = messages.create(test_db, test_email, test_message, source=test_source)
    assert message.id is not None
    assert message.email == test_email
    assert message.message == test_message
    assert message.source == test_source
    delete_from_db(test_db, message)
