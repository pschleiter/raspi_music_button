from .. import FakeAPlayAdapter


def test_version_of_aplay():
    assert FakeAPlayAdapter.get_version() == "1.2.4"
