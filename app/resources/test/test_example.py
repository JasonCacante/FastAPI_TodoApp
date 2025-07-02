def test_equal_or_not_equal():
    assert 1 == 1
    assert 2 != 3


def test_greater_than_or_less_than():
    assert 5 > 3
    assert 2 < 4


def test_is_instance():
    assert isinstance("Hello", str)
    assert not isinstance(123, str)


def test_boolean():
    validate = True
    assert validate is True
    assert ("hello" == "world") is False


def test_type():
    assert type(5) is int
    assert type("Hello") is not int


def test_list():
    my_list = [1, 2, 3]
    assert len(my_list) == 3
    assert my_list[0] == 1
    assert my_list[1] != 4
    assert 1 in my_list
    assert 7 not in my_list
