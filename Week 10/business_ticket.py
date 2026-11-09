from ticket import BAG_FEE, BAG_WEIGHT_KG, Ticket

FREE_BAG_ALLOWANCE = 2
LOUNGE_FEE = 80.0


class BusinessTicket(Ticket):
    """A premium ticket with free bags and optional lounge access."""

    TICKET_TYPE = 'Business'
    MAX_CHECKED_BAGS = 4

    def __init__(self, base_fare, lounge_access, checked_bag_count):
        super().__init__(base_fare, checked_bag_count)
        self.__lounge_access = lounge_access

    def calculate_price(self):
        # The first bags are free, anything after that is charged.
        paid_bags = max(0, self.get_checked_bag_count() - FREE_BAG_ALLOWANCE)
        price = self.get_base_fare() + paid_bags * BAG_FEE
        if self.__lounge_access:
            price += LOUNGE_FEE
        return price

    def baggage_allowance(self):
        return (f'You have {self.get_checked_bag_count()} x {BAG_WEIGHT_KG} '
                f'kg bags')

    def __str__(self):
        lounge = 'with' if self.__lounge_access else 'no'
        return (f'Business ticket: ${self.calculate_price():.2f}, '
                f'{self.get_checked_bag_count()} checked bag(s), '
                f'{lounge} lounge access')
