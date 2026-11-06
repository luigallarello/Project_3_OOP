"""Custom exceptions for the flight booking system.

Every error shares one parent, BookingSystemError, so the system can catch
any booking problem in one place. Errors are then grouped into four
categories:

BookingSystemError
    NotFoundError              - something doesn't exist
        BookingNotFoundError
        FlightNotFoundError
        PassengerNotRegisteredError
    InvalidStateError          - the action can't happen right now
        BookingStateError
        FlightNotBookableError
        FlightFullError
    InvalidValueError          - a value breaks a rule
        InvalidFareError
        InvalidBaggageError
        InvalidFlightStatusError
        EmptyBookingError
    ParticipationError         - an object can't take part in the action
        WrongObjectTypeError
        DuplicatePassengerError
"""


class BookingSystemError(Exception):
    """Parent of every error raised by the booking system."""


# Something doesn't exist.
class NotFoundError(BookingSystemError):
    """A booking, flight or passenger the system was asked for is missing."""


class BookingNotFoundError(NotFoundError):
    def __init__(self, booking_reference):
        self.booking_reference = booking_reference
        super().__init__(f'No booking found with reference '
                         f'{booking_reference!r}')


class FlightNotFoundError(NotFoundError):
    def __init__(self, flight_number):
        self.flight_number = flight_number
        super().__init__(f'Flight {flight_number} is not in the booking '
                         f'system')


class PassengerNotRegisteredError(NotFoundError):
    def __init__(self, passenger):
        self.passenger = passenger
        super().__init__(f'{passenger.get_name()} (passport '
                         f'{passenger.get_passport_number()}) is not '
                         f'registered')


# The action can't happen in the object's current state.
class InvalidStateError(BookingSystemError):
    """The object exists, but its current state doesn't allow the action."""


class BookingStateError(InvalidStateError):
    def __init__(self, booking_reference, action, reason):
        self.booking_reference = booking_reference
        self.action = action
        self.reason = reason
        super().__init__(f'Booking {booking_reference} cannot be {action}: '
                         f'{reason}')


class FlightNotBookableError(InvalidStateError):
    def __init__(self, flight_number, status):
        self.flight_number = flight_number
        self.status = status
        super().__init__(f'Flight {flight_number} is {status} and is not '
                         f'taking bookings')


class FlightFullError(InvalidStateError):
    def __init__(self, flight_number, seats_requested, seats_left):
        self.flight_number = flight_number
        self.seats_requested = seats_requested
        self.seats_left = seats_left
        super().__init__(f'Flight {flight_number} has {seats_left} seat(s) '
                         f'left but {seats_requested} were requested')


# A supplied value breaks a rule.
class InvalidValueError(BookingSystemError):
    """A value given to the system breaks one of its rules."""


class InvalidFareError(InvalidValueError):
    def __init__(self, base_fare):
        self.base_fare = base_fare
        super().__init__(f'Invalid base fare: {base_fare!r}. A fare must be '
                         f'a number of 0 or more')


class InvalidBaggageError(InvalidValueError):
    def __init__(self, ticket_type, bag_count, max_bags=None):
        self.ticket_type = ticket_type
        self.bag_count = bag_count
        self.max_bags = max_bags
        if max_bags is None:
            allowed = 'a whole number of 0 or more'
        else:
            allowed = f'0-{max_bags}'
        super().__init__(f'{ticket_type} only allows {allowed} checked '
                         f'bags, got {bag_count!r}')


class InvalidFlightStatusError(InvalidValueError):
    def __init__(self, status, valid_statuses):
        self.status = status
        self.valid_statuses = valid_statuses
        options = ', '.join(sorted(valid_statuses))
        super().__init__(f'Invalid flight status: {status!r}. Must be one '
                         f'of: {options}')


class EmptyBookingError(InvalidValueError):
    def __init__(self):
        super().__init__('A booking needs at least one passenger')


# An object can't take part in the requested operation.
class ParticipationError(BookingSystemError):
    """An object was given that can't take part in the operation."""


class WrongObjectTypeError(ParticipationError):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
        super().__init__(f'Expected a {expected} but got '
                         f'{type(received).__name__}: {received!r}')


class DuplicatePassengerError(ParticipationError):
    def __init__(self, passenger, booking_reference):
        self.passenger = passenger
        self.booking_reference = booking_reference
        super().__init__(f'{passenger.get_name()} (passport '
                         f'{passenger.get_passport_number()}) is already on '
                         f'booking {booking_reference}')
