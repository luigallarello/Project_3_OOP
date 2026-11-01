from flight import Flight


class TestFlightStatus:
    def test_constructor_keeps_a_valid_status(self, delayed_flight):
        assert delayed_flight.get_status() == 'delayed'

    def test_constructor_with_invalid_status_defaults_to_scheduled(
            self, capsys):
        flight = Flight('QF1', 'SYD', 'MEL', '10:00', 100, 'boarding')
        assert flight.get_status() == 'scheduled'
        assert 'Invalid flight status: boarding' in capsys.readouterr().out

    def test_status_can_be_set_to_scheduled(self, delayed_flight):
        delayed_flight.set_status('scheduled')
        assert delayed_flight.get_status() == 'scheduled'

    def test_status_can_be_set_to_delayed(self, scheduled_flight):
        scheduled_flight.set_status('delayed')
        assert scheduled_flight.get_status() == 'delayed'

    def test_status_can_be_set_to_departed(self, scheduled_flight):
        scheduled_flight.set_status('departed')
        assert scheduled_flight.get_status() == 'departed'

    def test_status_can_be_set_to_cancelled(self, scheduled_flight):
        scheduled_flight.set_status('cancelled')
        assert scheduled_flight.get_status() == 'cancelled'

    def test_invalid_status_is_rejected_and_old_status_kept(
            self, delayed_flight, capsys):
        delayed_flight.set_status('flying')
        assert delayed_flight.get_status() == 'delayed'
        assert 'Invalid flight status: flying' in capsys.readouterr().out

    def test_status_is_case_sensitive(self, scheduled_flight):
        scheduled_flight.set_status('CANCELLED')
        assert scheduled_flight.get_status() == 'scheduled'


class TestFlightString:
    def test_string_shows_route_time_status_and_seats(self,
                                                      scheduled_flight):
        assert str(scheduled_flight) == (
            'QF401: SYD -> MEL at 10:00 (scheduled, 3 seats)')

    def test_string_updates_after_status_change(self, scheduled_flight):
        scheduled_flight.set_status('delayed')
        assert '(delayed, 3 seats)' in str(scheduled_flight)
