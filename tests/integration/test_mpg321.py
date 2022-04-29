from .. import FakeMPG321Adapter


def test_version_of_mpg321():
    assert FakeMPG321Adapter.get_version() == "0.3.2"
