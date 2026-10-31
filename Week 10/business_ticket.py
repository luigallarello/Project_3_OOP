from ticket import Ticket

FREE_BAG_ALLOWANCE = 2
MAX_CHECKED_BAGS = 4
LOUNGE_FEE = 80.0
BAG_FEE = 35.0


class BusinessTicket(Ticket):
    def __init__(self, base_fare, lounge_access, checked_bag_count):
        super().__init__(base_fare)
        self.__lounge_access = lounge_access
        self.__checked_bag_count = checked_bag_count

    def get_lounge_access(self):
        return self.__lounge_access

    def set_lounge_access(self, lounge_access):
        if isinstance(lounge_access, bool):
            self.__lounge_access = lounge_access

    lounge_access = property(get_lounge_access, set_lounge_access)

    def get_checked_bag_count(self):
        return self.__checked_bag_count

    def set_checked_bag_count(self, checked_bag_count):
        if not 0 <= checked_bag_count <= MAX_CHECKED_BAGS:
            print(f'Business only allows 0-{MAX_CHECKED_BAGS} checked bags')
        self.__checked_bag_count = checked_bag_count

    checked_baggage_count = property(get_checked_bag_count,
                                     set_checked_bag_count)

    def calculate_price(self):
        # first 2 bags are free, anything after that is charged
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


# quick test, only runs when this file is run directly
if __name__ == '__main__':
    # 3 bags = 1 paid bag, plus lounge: 500 + 35 + 80 = 615
    ticket_1 = BusinessTicket(500.0, True, 3)
    print(ticket_1.calculate_price())
    print(ticket_1.baggage_allowance())
    print(ticket_1)

    ticket_2 = BusinessTicket(500.0, False, 1)
    print(ticket_2)
