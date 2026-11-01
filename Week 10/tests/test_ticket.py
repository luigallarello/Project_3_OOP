import pytest

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

    def test_negative_fare_is_rejected_and_fare_stays_zero(self, capsys):
        ticket = EconomyTicket(-1, 0)
        assert ticket.calculate_price() == pytest.approx(0.0)
        assert 'Invalid base fare' in capsys.readouterr().out

    def test_text_fare_is_rejected_and_fare_stays_zero(self, capsys):
        ticket = EconomyTicket('cheap', 0)
        assert ticket.calculate_price() == pytest.approx(0.0)
        assert 'Invalid base fare' in capsys.readouterr().out

    def test_none_fare_is_rejected_and_fare_stays_zero(self, capsys):
        ticket = EconomyTicket(None, 0)
        assert ticket.calculate_price() == pytest.approx(0.0)
        assert 'Invalid base fare' in capsys.readouterr().out

    def test_true_is_rejected_as_a_fare(self, capsys):
        # True counts as the number 1 in Python, so it needs its own check.
        ticket = EconomyTicket(True, 0)
        assert ticket.calculate_price() == pytest.approx(0.0)
        assert 'Invalid base fare' in capsys.readouterr().out

    def test_set_base_fare_rejects_bad_value_after_creation(self,
                                                            economy_ticket,
                                                            capsys):
        economy_ticket.set_base_fare(-50)
        assert economy_ticket.get_base_fare() == pytest.approx(250.0)
        assert 'Invalid base fare: -50' in capsys.readouterr().out
