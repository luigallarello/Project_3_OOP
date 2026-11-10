# Project_3_OOP

Flight booking system. A `BookingSystem` stores flights, passengers and bookings. A `Booking` holds a group of passengers on one flight with one ticket type, and tickets come in two kinds (`EconomyTicket` and `BusinessTicket`) built on an abstract `Ticket`.

22/10: Passenger and Flight classes

Today the `Passenger` class was written, and `Flight` was laid out straight after it. 

### Passenger

| Attribute | Type | Access |

|---|---|---|

| `name` | `str` | private, `get_name()` |
| `email` | `str` | private |
| `passport_number` | `str` | private, `get_passport_number()` |

`equals()` defines value equality for `Passenger`. Two objects are the same passenger if their passport numbers match, even if they are separate objects in memory. A passport number is unique to a person, so it's a better identity check than comparing names or object identity.

Since then: the setters were removed because nothing changes a passenger's details after they're created, and on 06/11 the constructor started checking that every detail is non-blank text.

28/10 Workshop 9-1: Code review with Billy

Billy went through my UML design and all of my proposed methods.

| Feedback | Why it matters |

|---|---|

| Dunder and magic methods (`__init__`, `__str__`) don't need to go in the UML | They're Python mechanics, not part of the design, and they clutter the diagram |
| A booking should be able to hold multiple passengers, but mine only stored one | A real booking often covers a family or group on the same flight |
| The Passenger -> BookingSystem relationship was wrong | The system keeps passengers it didn't create, so it's aggregation |
| The BookingSystem -> Booking relationship was wrong | The booking system creates and owns each booking, so it's composition, not aggregation |

29/10: Implementing the code review

Implemented Billy's changes from workshop 9-1. One booking can now hold a whole group of passengers.

| | Before | Now |

|---|---|---|

| Booking attribute | `passenger: Passenger` | `passengers: list[Passenger]` |
| Booking constructor | `Booking(booking_reference, booking_date, passenger, flight, ticket)` | `Booking(booking_reference, booking_date, passengers, flight, ticket)` |
| Getting passengers | `get_passenger()` returns one Passenger | `get_passengers()` returns a copy of the list |
| Adding passengers | not possible | `add_passenger(passenger)`, won't add the same passport twice |
| Creating a booking | `create_booking(passenger, flight, ticket)` | `create_booking(passengers, flight, ticket)`, takes a list or a single passenger |
| Seat check | none | `seats_booked(flight)` makes sure the whole group fits on the flight |
| UML Booking -> Passenger | 1 passenger | 1..* passengers |
| UML BookingSystem -> Booking | aggregation | composition |

### Why a list

A list keeps passengers in the order they were booked and makes it easy to count seats (`len()`) and add someone later. `get_passengers()` returns a copy so code outside `Booking` can't change the group without going through `add_passenger()`, which checks for duplicates.

### Why the seat check counts the whole group

Once a booking can hold several people, checking one seat isn't enough. `create_booking` now refuses the booking unless every passenger in the group fits.

31/10: PEP 8 and Week 10 folder

The Week 9 code was run through PEP 8 checks and a short demo was added to `main.py`. The code was then copied into a new Week 10 folder for the testing work.

01/11: Testing with pytest

A pytest suite was written for every class.

| File | What it tests |

|---|---|

| `tests/conftest.py` | Shared fixtures: three passengers plus a duplicate, one flight for each status plus small-capacity flights, both ticket types, ready-made bookings, and an empty and a filled booking system |
| `test_passenger.py` | Passport-based equality and the string output |
| `test_flight.py` | Valid and invalid statuses and the string output |
| `test_ticket.py` | `Ticket` can't be created directly, and base fare validation |
| `test_economy_ticket.py` / `test_business_ticket.py` | Prices, bag limits and boundaries (e.g. 2 free bags, 3rd is charged, 4 is the maximum) |
| `test_booking.py` | Adding passengers, confirming, cancelling and total cost |
| `test_booking_system.py` | Registering, creating bookings, every reason a booking is refused, seat counting, cancelling and available flights |
| `test_interactions.py` | Classes working together: both ticket types through `Booking`, bookings reacting to flight status, and full book, confirm and cancel workflows |

Writing the tests also meant cleaning up the code:

| Before | Now | Why |

|---|---|---|

| Quick checks under `if __name__ == '__main__':` in the class files | Moved into the pytest suite | The tests do the same job properly and can be rerun at any time |
| `set_booking_reference`, `get_booking_date`, `get_ticket` in `Booking` | Removed | Nothing in the program used them |
| Comments like `# list so one booking can cover a group` | Full sentences with a capital and a full stop | PEP 8 and rubric comment style |

Result: 144 tests passing, 100% statement and branch coverage (`coverage_report.txt`).

06/11: Exception handling

Today custom exceptions were added. Before this, a broken rule either returned `None`/`False` or printed a message and carried on, so the caller couldn't tell why something failed. Now the method that owns each rule raises a custom exception, and `BookingSystem` catches and reports it. Task 1 contains a list of all exceptions that were created. Wasn't able to get a code review this week.

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
| Bag count out of range or not a whole number | `Ticket.set_checked_bag_count` (shared by both ticket types) | `InvalidBaggageError` | ticket type, bad count, max bags |
| Flight status that doesn't exist (e.g. `'boarding'`) | `Flight.set_status` | `InvalidFlightStatusError` | bad status, list of valid ones |
| Changing a departed or cancelled flight to another status | `Flight.set_status` | `FlightStatusChangeError` | flight number, current status, new status |
| Negative or non-whole-number flight capacity | `Flight.__init__` | `InvalidCapacityError` | the bad capacity |
| Blank or non-text passenger name, email or passport | `Passenger.__init__` | `InvalidPassengerDetailsError` | which detail, the bad value |
| Adding a flight number that's already in the system | `BookingSystem.add_flight` | `DuplicateFlightError` | flight number |
| Booking with no passengers | `BookingSystem.create_booking` | `EmptyBookingError` | -|
| Wrong kind of object passed in (e.g. a string as a passenger) | `add_flight`, `register_passenger`, `create_booking`, `Booking.add_passenger` | `WrongObjectTypeError` | expected type, what was received |
| Same passenger added to a booking twice | `Booking.add_passenger` | `DuplicatePassengerError` | the passenger, booking reference |

### Task 2: Exception hierarchy (`exceptions.py`)

```
BookingSystemError(Exception)
├── NotFoundError          BookingNotFoundError, FlightNotFoundError, PassengerNotRegisteredError
├── InvalidStateError      BookingStateError, FlightNotBookableError, FlightFullError, FlightStatusChangeError
├── InvalidValueError      InvalidFareError, InvalidBaggageError, InvalidFlightStatusError, InvalidCapacityError,
│                          InvalidPassengerDetailsError, EmptyBookingError
└── ParticipationError     WrongObjectTypeError, DuplicatePassengerError, DuplicateFlightError
```

The four middle classes match the four kinds of problem in the task (doesn't exist, wrong state, bad value, can't take part). One shared parent means the system can catch every booking error with a single `except BookingSystemError`.

### Task 3: Raising

Every check runs before anything is changed, so a failed operation never leaves an object half-updated. For example `create_booking` checks passengers, ticket, flight and seats before it makes a reference or stores the booking, and the setters raise before storing the new value. 

Constructors use the setters, so an invalid `Flight` or `Ticket` is never created. Successful calls still return normally (`True`, the booking, etc.).

### Task 4: Handling

`BookingSystem` has `request_add_flight`, `request_register_passenger`, `request_booking`, `request_confirmation`, `request_cancellation`, `request_add_passenger` and `request_flight_status_change`. Each one wraps the core operation in `try`/`except BookingSystemError`, prints `Could not <action>: <reason>`, adds the message to an error log (`get_error_log()`), and returns `None` so the program keeps going. `main.py` has no `try`/`except`; it only calls these methods.

| Before | Now |
|---|---|
| `create_booking` returned `None` on failure | raises the matching custom exception |
| `cancel_booking` returned `None` on failure | raises `BookingNotFoundError` / `BookingStateError` |
| `confirm_booking` / `cancel_booking` / `add_passenger` returned `False` | raise `BookingStateError` / `DuplicatePassengerError` / `WrongObjectTypeError` |
| setters printed a message and kept a default | raise `InvalidFareError` / `InvalidBaggageError` / `InvalidFlightStatusError` |
| `add_flight` / `register_passenger` silently ignored bad objects | raise `WrongObjectTypeError` |
| adding a flight number twice silently replaced the old flight | raises `DuplicateFlightError` |
| `Flight` capacity and `Passenger` details weren't checked | raise `InvalidCapacityError` / `InvalidPassengerDetailsError` |
| a departed flight could be set back to scheduled | raises `FlightStatusChangeError` |
| cancelled bookings were tracked in a separate `set`, so cancelling through `Booking` didn't free the seat | the booking's own status is the only record (`Booking.is_cancelled()`) |
| status strings like `'pending'` were typed out in several files | class constants (`Booking.PENDING`, `Flight.DEPARTED`, `Flight.BOOKABLE_STATUSES`) |
| both ticket types stored and checked bags separately | `Ticket` stores and checks `checked_bag_count`; each type sets `MAX_CHECKED_BAGS` |
| `Booking.equals` was never used by the program | removed |
| no safe way to call these from the program | `request_*` methods catch, report and log |
| adding a passenger to a booking skipped the seat check | `add_passenger_to_booking` checks seats first |

### Task 5: Testing

Old tests that expected `None`/`False`/printed messages now use `pytest.raises()` and still check the object state is unchanged afterwards. `tests/test_exceptions.py` covers the hierarchy, new lookups, `add_passenger_to_booking`, and the handled `request_*` methods (they return `None`, log the message and leave the system unchanged). 220 tests pass, 100% statement and branch coverage (`coverage_report.txt`).

### Task 6: Demo

Finally a demo was created under the name of `python3 main.py`. It makes normal bookings, triggers twelve handled problems, shows nothing changed, then keeps using the system (adds a passenger, cancels, rebooks, lists available flights).
