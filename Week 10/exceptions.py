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
        FlightStatusChangeError
    InvalidValueError          - a value breaks a rule
        InvalidFareError
        InvalidBaggageError
        InvalidFlightStatusError
        InvalidCapacityError
        InvalidPassengerDetailsError
        EmptyBookingError
    ParticipationError         - an object can't take part in the action
        WrongObjectTypeError
        DuplicatePassengerError
        DuplicateFlightError
"""


class BookingSystemError(Exception):
    """Parent of every error raised by the booking system."""


# Something doesn't exist.
class NotFoundError(BookingSystemError):
    """A booking, flight or passenger the system was asked for is missing."""


class BookingNotFoundError(NotFoundError):
    """No booking is stored under the given reference."""

    def __init__(self, booking_reference):
        self.booking_reference = booking_reference
        super().__init__(f'No booking found with reference '
                         f'{booking_reference!r}')


class FlightNotFoundError(NotFoundError):
    """The flight hasn't been added to the booking system."""

    def __init__(self, flight_number):
        self.flight_number = flight_number
        super().__init__(f'Flight {flight_number} is not in the booking '
                         f'system')


class PassengerNotRegisteredError(NotFoundError):
    """The passenger hasn't been registered with the booking system."""

    def __init__(self, passenger):
        self.passenger = passenger
        super().__init__(f'{passenger.get_name()} (passport '
                         f'{passenger.get_passport_number()}) is not '
                         f'registered')


# The action can't happen in the object's current state.
class InvalidStateError(BookingSystemError):
    """The object exists, but its current state doesn't allow the action."""


class BookingStateError(InvalidStateError):
    """A booking can't be confirmed, cancelled or changed right now."""

    def __init__(self, booking_reference, action, reason):
        self.booking_reference = booking_reference
        self.action = action
        self.reason = reason
        super().__init__(f'Booking {booking_reference} cannot be {action}: '
                         f'{reason}')


class FlightNotBookableError(InvalidStateError):
    """The flight has departed or been cancelled, so it can't be booked."""

    def __init__(self, flight_number, status):
        self.flight_number = flight_number
        self.status = status
        super().__init__(f'Flight {flight_number} is {status} and is not '
                         f'taking bookings')


class FlightFullError(InvalidStateError):
    """There aren't enough seats left for the passengers requested."""

    def __init__(self, flight_number, seats_requested, seats_left):
        self.flight_number = flight_number
        self.seats_requested = seats_requested
        self.seats_left = seats_left
        super().__init__(f'Flight {flight_number} has {seats_left} seat(s) '
                         f'left but {seats_requested} were requested')


class FlightStatusChangeError(InvalidStateError):
    """A departed or cancelled flight can't change to another status."""

    def __init__(self, flight_number, current_status, new_status):
        self.flight_number = flight_number
        self.current_status = current_status
        self.new_status = new_status
        super().__init__(f'Flight {flight_number} is {current_status} and '
                         f'cannot be changed to {new_status}')


# A supplied value breaks a rule.
class InvalidValueError(BookingSystemError):
    """A value given to the system breaks one of its rules."""


class InvalidFareError(InvalidValueError):
    """A ticket's base fare is negative or isn't a number."""

    def __init__(self, base_fare):
        self.base_fare = base_fare
        super().__init__(f'Invalid base fare: {base_fare!r}. A fare must be '
                         f'a number of 0 or more')


class InvalidBaggageError(InvalidValueError):
    """A checked bag count is out of range or isn't a whole number."""

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
    """The status given isn't one a flight can have."""

    def __init__(self, status, valid_statuses):
        self.status = status
        self.valid_statuses = valid_statuses
        options = ', '.join(sorted(valid_statuses))
        super().__init__(f'Invalid flight status: {status!r}. Must be one '
                         f'of: {options}')


class InvalidCapacityError(InvalidValueError):
    """A flight's seat capacity is negative or isn't a whole number."""

    def __init__(self, capacity):
        self.capacity = capacity
        super().__init__(f'Invalid capacity: {capacity!r}. Capacity must be '
                         f'a whole number of 0 or more')


class InvalidPassengerDetailsError(InvalidValueError):
    """A passenger's name, email or passport number is blank or not text."""

    def __init__(self, field, value):
        self.field = field
        self.value = value
        super().__init__(f'Invalid passenger {field}: {value!r}. It must be '
                         f'text that isn\'t blank')


class EmptyBookingError(InvalidValueError):
    """A booking was requested with no passengers on it."""

    def __init__(self):
        super().__init__('A booking needs at least one passenger')


# An object can't take part in the requested operation.
class ParticipationError(BookingSystemError):
    """An object was given that can't take part in the operation."""


class WrongObjectTypeError(ParticipationError):
    """An object of the wrong class was passed in."""

    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
        super().__init__(f'Expected a {expected} but got '
                         f'{type(received).__name__}: {received!r}')


class DuplicatePassengerError(ParticipationError):
    """The passenger is already on the booking."""

    def __init__(self, passenger, booking_reference):
        self.passenger = passenger
        self.booking_reference = booking_reference
        super().__init__(f'{passenger.get_name()} (passport '
                         f'{passenger.get_passport_number()}) is already on '
                         f'booking {booking_reference}')


class DuplicateFlightError(ParticipationError):
    """A flight with the same number is already in the system."""

    def __init__(self, flight_number):
        self.flight_number = flight_number
        super().__init__(f'Flight {flight_number} is already in the booking '
                         f'system')
