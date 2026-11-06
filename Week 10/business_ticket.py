from exceptions import InvalidBaggageError
from ticket import BAG_FEE, Ticket

FREE_BAG_ALLOWANCE = 2
MAX_CHECKED_BAGS = 4
LOUNGE_FEE = 80.0


class BusinessTicket(Ticket):
    def __init__(self, base_fare, lounge_access, checked_bag_count):
        super().__init__(base_fare)
        self.__lounge_access = lounge_access
        # Start at zero, then let the setter check the real value.
        self.__checked_bag_count = 0
        self.set_checked_bag_count(checked_bag_count)

    def set_checked_bag_count(self, checked_bag_count):
        is_valid = (isinstance(checked_bag_count, int)
                    and 0 <= checked_bag_count <= MAX_CHECKED_BAGS)
        if not is_valid:
            # Raise before changing anything so the old count is kept.
            raise InvalidBaggageError('Business', checked_bag_count,
                                      MAX_CHECKED_BAGS)
        self.__checked_bag_count = checked_bag_count

    def calculate_price(self):
        # The first bags are free, anything after that is charged.
        paid_bags = max(0, self.__checked_bag_count - FREE_BAG_ALLOWANCE)
        price = self.get_base_fare() + paid_bags * BAG_FEE
        if self.__lounge_access:
            price += LOUNGE_FEE
        return price

    def baggage_allowance(self):
        return f'You have {self.__checked_bag_count} x 23 kg bags'

    def __str__(self):
        lounge = 'with' if self.__lounge_access else 'no'
        return (f'Business ticket: ${self.calculate_price():.2f}, '
                f'{self.__checked_bag_count} checked bag(s), '
                f'{lounge} lounge access')
