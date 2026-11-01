import pytest

from booking import Booking
from booking_system import BookingSystem
from business_ticket import BusinessTicket
from economy_ticket import EconomyTicket
from flight import Flight
from passenger import Passenger


# Passengers.
@pytest.fixture
def lui():
    return Passenger('Lui', 'lui@email.com', 'PA123456')


@pytest.fixture
def sam():
    return Passenger('Sam', 'sam@email.com', 'PB654321')


@pytest.fixture
def alex():
    return Passenger('Alex', 'alex@email.com', 'PC111222')


@pytest.fixture
def lui_duplicate():
    # A different object with the same passport number as lui.
    return Passenger('Lui G', 'other@email.com', 'PA123456')


# Flights, one for each status plus a small one for capacity tests.
@pytest.fixture
def scheduled_flight():
    return Flight('QF401', 'SYD', 'MEL', '10:00', 3, 'scheduled')


@pytest.fixture
def delayed_flight():
    return Flight('QF643', 'SYD', 'PER', '15:30', 150, 'delayed')


@pytest.fixture
def cancelled_flight():
    return Flight('QF500', 'SYD', 'BNE', '12:00', 100, 'cancelled')


@pytest.fixture
def departed_flight():
    return Flight('QF900', 'SYD', 'ADL', '06:00', 100, 'departed')


@pytest.fixture
def two_seat_flight():
    return Flight('QF222', 'SYD', 'CBR', '09:00', 2, 'scheduled')


# Tickets.
@pytest.fixture
def economy_ticket():
    return EconomyTicket(250.0, 1)


@pytest.fixture
def business_ticket():
    return BusinessTicket(500.0, True, 3)


@pytest.fixture
def business_ticket_no_lounge():
    return BusinessTicket(500.0, False, 1)


# Bookings, built directly so Booking is tested without BookingSystem.
@pytest.fixture
def booking(lui, scheduled_flight, economy_ticket):
    return Booking('BK0001', '2026-10-31', [lui],
                   scheduled_flight, economy_ticket)


@pytest.fixture
def group_booking(lui, sam, scheduled_flight, economy_ticket):
    return Booking('BK0002', '2026-10-31', [lui, sam],
                   scheduled_flight, economy_ticket)


@pytest.fixture
def departed_booking(lui, departed_flight, economy_ticket):
    return Booking('BK0003', '2026-10-31', [lui],
                   departed_flight, economy_ticket)


# Booking systems, one empty and one that already has data registered.
@pytest.fixture
def empty_system():
    return BookingSystem()


@pytest.fixture
def system(empty_system, lui, sam, alex, scheduled_flight, delayed_flight,
           cancelled_flight, departed_flight):
    for passenger in (lui, sam, alex):
        empty_system.register_passenger(passenger)
    for flight in (scheduled_flight, delayed_flight, cancelled_flight,
                   departed_flight):
        empty_system.add_flight(flight)
    return empty_system
