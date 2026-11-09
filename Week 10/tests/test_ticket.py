import pytest

from exceptions import InvalidBaggageError, InvalidFareError
from economy_ticket import EconomyTicket
from ticket import Ticket


class TestTicketIsAbstract:
    def test_plain_ticket_cannot_be_created(self):
        with pytest.raises(TypeError):
            Ticket(100.0)

    def test_subclass_missing_abstract_methods_cannot_be_created(self):
        class HalfTicket(Ticket):
            def calculate_price(self):
                return 0.0

        with pytest.raises(TypeError):
            HalfTicket(100.0)


class TestBaseFareValidation:
    # Base fare validation is shared by every ticket, so EconomyTicket with
    # no bags is used here to read the fare back through calculate_price().
    def test_float_fare_is_kept(self):
        assert EconomyTicket(199.99, 0).calculate_price() == pytest.approx(
            199.99)

    def test_whole_number_fare_is_accepted(self):
        assert EconomyTicket(100, 0).calculate_price() == pytest.approx(100.0)

    def test_zero_fare_is_allowed(self):
        assert EconomyTicket(0, 0).calculate_price() == pytest.approx(0.0)

    @pytest.mark.parametrize('bad_fare', [-1, 'cheap', None])
    def test_bad_fare_raises_when_creating_a_ticket(self, bad_fare):
        with pytest.raises(InvalidFareError) as error:
            EconomyTicket(bad_fare, 0)
        assert error.value.base_fare == bad_fare

    def test_true_is_rejected_as_a_fare(self):
        # True counts as the number 1 in Python, so it needs its own check.
        with pytest.raises(InvalidFareError):
            EconomyTicket(True, 0)

    def test_smallest_negative_fare_is_rejected(self):
        # Boundary: just below the lowest allowed fare of 0.
        with pytest.raises(InvalidFareError):
            EconomyTicket(-0.01, 0)

    def test_set_base_fare_rejects_bad_value_after_creation(self,
                                                            economy_ticket):
        with pytest.raises(InvalidFareError, match='Invalid base fare: -50'):
            economy_ticket.set_base_fare(-50)
        # The failed change leaves the old fare in place.
        assert economy_ticket.get_base_fare() == pytest.approx(250.0)


class TestSharedBagCount:
    # Both ticket types store and check their bags through Ticket.
    def test_both_types_report_their_bag_count(self, economy_ticket,
                                               business_ticket):
        assert economy_ticket.get_checked_bag_count() == 1
        assert business_ticket.get_checked_bag_count() == 3

    def test_economy_bag_count_can_be_changed(self, economy_ticket):
        economy_ticket.set_checked_bag_count(3)
        assert economy_ticket.calculate_price() == pytest.approx(355.0)

    def test_each_type_names_itself_in_the_error(self, economy_ticket,
                                                 business_ticket):
        with pytest.raises(InvalidBaggageError, match='^Economy'):
            economy_ticket.set_checked_bag_count(-1)
        with pytest.raises(InvalidBaggageError, match='^Business'):
            business_ticket.set_checked_bag_count(5)
