from exceptions import InvalidBaggageError
from ticket import BAG_FEE, Ticket


class EconomyTicket(Ticket):
    def __init__(self, base_fare, checked_bag_count):
        super().__init__(base_fare)
        # Economy has no upper limit (every bag is paid for), but the
        # count still has to be a whole number that isn't negative.
        is_valid = (isinstance(checked_bag_count, int)
                    and not isinstance(checked_bag_count, bool)
                    and checked_bag_count >= 0)
        if not is_valid:
            raise InvalidBaggageError('Economy', checked_bag_count)
        self.__checked_bag_count = checked_bag_count

    def calculate_price(self):
        # Economy pays the bag fee for every checked bag.
        return self.get_base_fare() + self.__checked_bag_count * BAG_FEE

    def baggage_allowance(self):
        return f'You have {self.__checked_bag_count} x 23 kg checked bags'

    def __str__(self):
        return (f'Economy ticket: ${self.calculate_price():.2f}, '
                f'{self.__checked_bag_count} checked bag(s)')
