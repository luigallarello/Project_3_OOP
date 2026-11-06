import pytest

from exceptions import InvalidBaggageError
from business_ticket import BusinessTicket
from ticket import Ticket


class TestBusinessPrice:
    def test_price_includes_paid_bag_and_lounge(self, business_ticket):
        # 500 fare + 1 paid bag ($35) + lounge ($80).
        assert business_ticket.calculate_price() == pytest.approx(615.0)

    def test_price_without_lounge(self, business_ticket_no_lounge):
        assert business_ticket_no_lounge.calculate_price() == pytest.approx(
            500.0)

    def test_no_bags_means_just_the_fare(self):
        ticket = BusinessTicket(500.0, False, 0)
        assert ticket.calculate_price() == pytest.approx(500.0)

    def test_two_bags_are_still_free(self):
        # Boundary: the last free bag.
        ticket = BusinessTicket(500.0, False, 2)
        assert ticket.calculate_price() == pytest.approx(500.0)

    def test_third_bag_is_the_first_one_charged(self):
        # Boundary: the first paid bag.
        ticket = BusinessTicket(500.0, False, 3)
        assert ticket.calculate_price() == pytest.approx(535.0)

    def test_four_bags_is_the_maximum_and_is_allowed(self):
        # Boundary: the most bags a business ticket can have.
        ticket = BusinessTicket(500.0, False, 4)
        assert ticket.calculate_price() == pytest.approx(570.0)

    def test_lounge_adds_the_same_fee_at_any_bag_count(self):
        with_lounge = BusinessTicket(500.0, True, 0).calculate_price()
        without_lounge = BusinessTicket(500.0, False, 0).calculate_price()
        assert with_lounge - without_lounge == pytest.approx(80.0)


class TestBusinessBagLimits:
    def test_five_bags_is_rejected(self):
        # Boundary: one more than the maximum.
        with pytest.raises(InvalidBaggageError) as error:
            BusinessTicket(500.0, False, 5)
        assert 'Business only allows 0-4 checked bags' in str(error.value)
        assert error.value.bag_count == 5
        assert error.value.max_bags == 4

    @pytest.mark.parametrize('bad_count', [-1, 'two', 2.5])
    def test_bad_bag_counts_are_rejected(self, bad_count):
        with pytest.raises(InvalidBaggageError, match='Business only allows'):
            BusinessTicket(500.0, False, bad_count)

    def test_changing_to_a_bad_count_keeps_the_old_count(self,
                                                         business_ticket):
        with pytest.raises(InvalidBaggageError):
            business_ticket.set_checked_bag_count(9)
        assert business_ticket.baggage_allowance() == (
            'You have 3 x 23 kg bags')
        assert business_ticket.calculate_price() == pytest.approx(615.0)

    def test_changing_to_a_valid_count_updates_the_price(self,
                                                         business_ticket):
        business_ticket.set_checked_bag_count(4)
        assert business_ticket.calculate_price() == pytest.approx(650.0)


class TestBusinessDescriptions:
    def test_baggage_allowance_mentions_bag_count(self, business_ticket):
        assert business_ticket.baggage_allowance() == (
            'You have 3 x 23 kg bags')

    def test_string_with_lounge(self, business_ticket):
        assert str(business_ticket) == (
            'Business ticket: $615.00, 3 checked bag(s), with lounge access')

    def test_string_without_lounge(self, business_ticket_no_lounge):
        assert str(business_ticket_no_lounge) == (
            'Business ticket: $500.00, 1 checked bag(s), no lounge access')

    def test_is_a_ticket(self, business_ticket):
        assert isinstance(business_ticket, Ticket)
