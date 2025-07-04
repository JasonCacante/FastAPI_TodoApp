import pytest


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


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_student():
    return Student("John", "Doe", "Computer Science", 3)


def test_student_class(default_student):
    assert default_student.first_name == "John"
    assert default_student.last_name == "Doe"
    assert default_student.major == "Computer Science"
    assert default_student.years == 3

    # Test attributes
    assert hasattr(default_student, "first_name")
    assert hasattr(default_student, "last_name")
    assert hasattr(default_student, "major")
    assert hasattr(default_student, "years")

    # Test attribute types
    assert isinstance(default_student.first_name, str)
    assert isinstance(default_student.last_name, str)
    assert isinstance(default_student.major, str)
    assert isinstance(default_student.years, int)
