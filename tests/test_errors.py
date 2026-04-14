from zork.errors import ZorkError


def test_zork_error_attributes():
    err = ZorkError(400, "Bad request")
    assert err.status_code == 400
    assert err.message == "Bad request"
    assert str(err) == "Bad request"


def test_zork_error_cancel_delete():
    err = ZorkError.cancel_delete()
    assert err.status_code == 200
    assert err.message == "__cancel_delete__"
