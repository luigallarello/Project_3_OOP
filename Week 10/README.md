# Project_3_OOP


22/10:
Today the passenger class is being written up. It includes three attributes: name, email and passport number. All of these are private and should be processed as strings. Each of the attributes have getters and setters and there is one additional method called 'equals'.

equals() defines value equality for Passenger. Two objects represent the same passenger if their passport numbers match, regardless of whether they are in the same object of memory.

28/10 Workshop 9-1: Code review with Billy:
Todays code review billy went over my uml design with all of my proposed methods etc. He noted I didn't need dunder and magic methods in my uml. He also noted that a booking can hold multiple passengers rather than just one, and my current booking only stores one passenger. He noted a few relationship changes on the uml as well, in specific the passenger -> bookingsystem and booking system to booking. This is because the booking system creates the booking but is listed as the wrong relationship.

29/10:
Implemented changes billy wanted from code review in workshop 9-1. Multiple passengers can now be booked under one booking.

Passenger changes (before -> now):

| | Before | Now |
|---|---|---|
| Booking attribute | `passenger: Passenger` | `passengers: list[Passenger]` |
| Booking constructor | `Booking(booking_reference, booking_date, passenger, flight, ticket)` | `Booking(booking_reference, booking_date, passengers, flight, ticket)` |
| Getting passengers | `get_passenger()` returns one Passenger | `get_passengers()` returns a list of Passengers |
| Adding passengers | not possible | `add_passenger(passenger)` adds someone, won't add the same passport twice |
| Creating a booking | `create_booking(passenger, flight, ticket)` | `create_booking(passengers, flight, ticket)`, takes a list or a single passenger |
| Seat check | none | `seats_booked(flight)` makes sure the whole group fits on the flight |
| UML Booking -> Passenger | 1 passenger | 1..* passengers |
| UML BookingSystem -> Booking | aggregation | composition |

06/11: Exception handling

This adds custom exceptions. Before this, a broken rule either returned `None`/`False` or printed a message and carried on, so the caller couldn't tell *why* something failed. Now the method that owns each rule raises a custom exception, and `BookingSystem` catches and reports it.

### Task 1: Exceptional situations

| Situation | Where it's checked | Exception | Useful information carried |
|---|---|---|---|
| Booking reference doesn't exist | `BookingSystem.get_booking` | `BookingNotFoundError` | the reference that was asked for |
| Flight isn't in the system | `BookingSystem.get_flight` | `FlightNotFoundError` | flight number |
| Passenger hasn't been registered | `BookingSystem.create_booking` / `add_passenger_to_booking` | `PassengerNotRegisteredError` | the passenger (name + passport) |
| Confirming a booking that isn't pending, or whose flight is cancelled/departed | `Booking.confirm_booking` | `BookingStateError` | reference, action, reason |
| Cancelling a booking that's already cancelled, or after the flight departed | `Booking.cancel_booking` | `BookingStateError` | reference, action, reason |
| Adding someone to a cancelled booking | `Booking.add_passenger` | `BookingStateError` | reference, action, reason |
| Booking a cancelled or departed flight | `BookingSystem.create_booking` | `FlightNotBookableError` | flight number, status |
| Group is bigger than the seats left | `BookingSystem.create_booking` / `add_passenger_to_booking` | `FlightFullError` | flight number, seats requested, seats left |
| Negative / non-number fare | `Ticket.set_base_fare` | `InvalidFareError` | the bad fare |
| Bag count out of range or not a whole number | `BusinessTicket.set_checked_bag_count`, `EconomyTicket.__init__` | `InvalidBaggageError` | ticket type, bad count, max bags |
| Flight status that doesn't exist (e.g. `'boarding'`) | `Flight.set_status` | `InvalidFlightStatusError` | bad status, list of valid ones |
| Booking with no passengers | `BookingSystem.create_booking` | `EmptyBookingError` | - |
| Wrong kind of object passed in (e.g. a string as a passenger) | `add_flight`, `register_passenger`, `create_booking`, `Booking.add_passenger` | `WrongObjectTypeError` | expected type, what was received |
| Same passenger added to a booking twice | `Booking.add_passenger` | `DuplicatePassengerError` | the passenger, booking reference |

### Task 2: Exception hierarchy (`exceptions.py`)

```
BookingSystemError(Exception)
├── NotFoundError          BookingNotFoundError, FlightNotFoundError, PassengerNotRegisteredError
├── InvalidStateError      BookingStateError, FlightNotBookableError, FlightFullError
├── InvalidValueError      InvalidFareError, InvalidBaggageError, InvalidFlightStatusError, EmptyBookingError
└── ParticipationError     WrongObjectTypeError, DuplicatePassengerError
```

The four middle classes match the four kinds of problem in the task (doesn't exist, wrong state, bad value, can't take part). One shared parent means the system can catch every booking error with a single `except BookingSystemError`.

### Task 3: Raising

Every check runs before anything is changed, so a failed operation never leaves an object half-updated. For example `create_booking` checks passengers, ticket, flight and seats before it makes a reference or stores the booking, and the setters raise before storing the new value. Constructors use the setters, so an invalid `Flight` or `Ticket` is never created. Successful calls still return normally (`True`, the booking, etc.).

### Task 4: Handling

`BookingSystem` has `request_booking`, `request_confirmation`, `request_cancellation`, `request_add_passenger` and `request_flight_status_change`. Each one wraps the core operation in `try`/`except BookingSystemError`, prints `Could not <action>: <reason>`, adds the message to an error log (`get_error_log()`), and returns `None` so the program keeps going. `main.py` has no `try`/`except`; it only calls these methods.

| Before | Now |
|---|---|
| `create_booking` returned `None` on failure | raises the matching custom exception |
| `cancel_booking` returned `None` on failure | raises `BookingNotFoundError` / `BookingStateError` |
| `confirm_booking` / `cancel_booking` / `add_passenger` returned `False` | raise `BookingStateError` / `DuplicatePassengerError` / `WrongObjectTypeError` |
| setters printed a message and kept a default | raise `InvalidFareError` / `InvalidBaggageError` / `InvalidFlightStatusError` |
| `add_flight` / `register_passenger` silently ignored bad objects | raise `WrongObjectTypeError` |
| no safe way to call these from the program | `request_*` methods catch, report and log |
| adding a passenger to a booking skipped the seat check | `add_passenger_to_booking` checks seats first |

### Task 5: Testing

Old tests that expected `None`/`False`/printed messages now use `pytest.raises()` and still check the object state is unchanged afterwards. `tests/test_exceptions.py` covers the hierarchy, new lookups, `add_passenger_to_booking`, and the handled `request_*` methods (they return `None`, log the message and leave the system unchanged). 193 tests pass, 100% statement and branch coverage (`coverage_report.txt`).

### Task 6: Demo

Run `python3 main.py`. It makes normal bookings, triggers nine handled problems, shows nothing changed, then keeps using the system (adds a passenger, cancels, rebooks, lists available flights).
