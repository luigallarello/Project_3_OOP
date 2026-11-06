from booking_system import BookingSystem
from business_ticket import BusinessTicket
from economy_ticket import EconomyTicket
from flight import Flight
from passenger import Passenger


def heading(title):
    print(f'\n--- {title} ---')


system = BookingSystem()

sydney_melbourne = Flight('QF401', 'SYD', 'MEL', '10:00', 3, 'scheduled')
sydney_perth = Flight('QF643', 'SYD', 'PER', '15:30', 150, 'delayed')
sydney_brisbane = Flight('QF500', 'SYD', 'BNE', '12:00', 100, 'cancelled')

lui = Passenger('Lui', 'lui@email.com', 'PA123456')
sam = Passenger('Sam', 'sam@email.com', 'PB654321')
alex = Passenger('Alex', 'alex@email.com', 'PC111222')
stranger = Passenger('Bob', 'bob@email.com', 'PZ999999')  # not registered

# Both are Tickets, so Booking can use either one (abstraction and
# polymorphism from earlier weeks).
economy = EconomyTicket(250.0, 1)
business = BusinessTicket(500.0, True, 3)

for flight in (sydney_melbourne, sydney_perth, sydney_brisbane):
    system.add_flight(flight)
for passenger in (lui, sam, alex):
    system.register_passenger(passenger)

heading('Normal bookings')
group = system.request_booking([lui, sam], sydney_melbourne, economy)
print(f'Total cost: ${group.total_cost():.2f}')
perth_trip = system.request_booking(alex, sydney_perth, business)
print(f'Total cost: ${perth_trip.total_cost():.2f}')
system.request_confirmation('BK0001')
print(system)

heading('Problems the system catches')
# Each of these raises a custom exception inside BookingSystem. The
# system handles it, prints why it failed and returns None.
system.request_booking(stranger, sydney_melbourne, economy)
system.request_booking(lui, sydney_brisbane, economy)
system.request_booking([alex, lui], sydney_melbourne, economy)
system.request_booking([], sydney_melbourne, economy)
system.request_confirmation('BK0001')
system.request_cancellation('BK0099')
system.request_add_passenger('BK0001', lui)
system.request_flight_status_change('QF643', 'boarding')

heading('Nothing was changed by the failed requests')
print(system)
print(group)
print(f'Seats booked on QF401: {system.seats_booked(sydney_melbourne)}')
print(f'QF643 status is still: {sydney_perth.get_status()}')

heading('The program carries on')
system.request_add_passenger('BK0001', alex)
print(f'Seats booked on QF401: {system.seats_booked(sydney_melbourne)}')
system.request_cancellation('BK0001')
replacement = system.request_booking(lui, sydney_melbourne, economy)
print('Available flights:')
for flight in system.get_available_flights():
    print(f'  {flight}')

heading('Departed flights block cancellation')
system.request_flight_status_change('QF643', 'departed')
system.request_cancellation('BK0002')
print(perth_trip)

heading(f'Error log ({len(system.get_error_log())} handled problems)')
for number, message in enumerate(system.get_error_log(), start=1):
    print(f'{number}. {message}')
