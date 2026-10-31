from booking_system import BookingSystem
from economy_ticket import EconomyTicket
from flight import Flight
from passenger import Passenger

system = BookingSystem()

flight = Flight('QF401', 'SYD', 'MEL', '10:00', 180, 'scheduled')
lui = Passenger('Lui', 'lui@email.com', 'PA123456')
sam = Passenger('Sam', 'sam@email.com', 'PB654321')
ticket = EconomyTicket(250.0, 1)

system.add_flight(flight)
system.register_passenger(lui)
system.register_passenger(sam)

booking = system.create_booking([lui, sam], flight, ticket)
print(booking)
print(booking.total_cost())

booking.confirm_booking()
print(booking)

system.cancel_booking('BK0001')
print(booking)
print(system)
