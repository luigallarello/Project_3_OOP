import pytest

from economy_ticket import EconomyTicket
from ticket import Ticket


class TestEconomyPrice:
    def test_price_is_fare_plus_bag_fee(self, economy_ticket):
        # The $250 fare plus one bag at $35.
        assert economy_ticket.calculate_price() == pytest.approx(285.0)

    def test_no_bags_means_just_the_fare(self):
        ticket = EconomyTicket(250.0, 0)
        assert ticket.calculate_price() == pytest.approx(250.0)

    def test_two_bags_are_both_charged(self):
        ticket = EconomyTicket(250.0, 2)
        assert ticket.calculate_price() == pytest.approx(320.0)

    def test_five_bags_are_all_charged(self):
        ticket = EconomyTicket(250.0, 5)
        assert ticket.calculate_price() == pytest.approx(425.0)

    def test_price_with_awkward_decimals(self):
        # Floating point maths, so approx is needed.
        ticket = EconomyTicket(2325.22, 2)
        assert ticket.calculate_price() == pytest.approx(2395.22)


class TestEconomyDescriptions:
    def test_baggage_allowance_mentions_bag_count(self, economy_ticket):
        assert economy_ticket.baggage_allowance() == (
            'You have 1 x 23 kg checked bags')

    def test_string_shows_price_and_bags(self, economy_ticket):
        assert str(economy_ticket) == (
            'Economy ticket: $285.00, 1 checked bag(s)')

    def test_is_a_ticket(self, economy_ticket):
        assert isinstance(economy_ticket, Ticket)
