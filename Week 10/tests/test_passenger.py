import pytest

from exceptions import InvalidPassengerDetailsError
from passenger import Passenger


class TestPassengerEquals:
    def test_same_passport_different_objects_are_equal(self, lui,
                                                       lui_duplicate):
        assert lui is not lui_duplicate
        assert lui.equals(lui_duplicate)

    def test_equality_works_in_both_directions(self, lui, lui_duplicate):
        assert lui_duplicate.equals(lui)

    def test_different_passport_is_not_equal(self, lui, sam):
        assert not lui.equals(sam)

    def test_passenger_equals_itself(self, lui):
        assert lui.equals(lui)

    def test_non_passenger_is_not_equal(self, lui):
        assert not lui.equals('PA123456')
        assert not lui.equals(None)


class TestPassengerString:
    def test_string_shows_all_details(self, lui):
        text = str(lui)
        assert 'Lui' in text
        assert 'lui@email.com' in text
        assert 'PA123456' in text


class TestPassengerValidation:
    @pytest.mark.parametrize('field, details', [
        ('name', ('', 'lui@email.com', 'PA123456')),
        ('name', ('   ', 'lui@email.com', 'PA123456')),
        ('email', ('Lui', None, 'PA123456')),
        ('passport number', ('Lui', 'lui@email.com', 123456)),
    ])
    def test_bad_details_are_rejected(self, field, details):
        with pytest.raises(InvalidPassengerDetailsError) as error:
            Passenger(*details)
        assert error.value.field == field
        assert f'Invalid passenger {field}' in str(error.value)
