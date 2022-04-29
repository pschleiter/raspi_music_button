from .. import FakeAMixerAdapter


def test_version_of_amixer():
    assert FakeAMixerAdapter.get_version() == "1.2.4"
