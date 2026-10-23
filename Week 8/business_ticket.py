from ticket import Ticket

FREE_BAG_ALLOWANCE = 2
MAX_CHECKED_BAGS = 4
LOUNGE_FEE = 80.0
BAG_FEE =  35.0

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
        if not 0 <= checked_bag_count <= BusinessTicket.MAX_CHECKED_BAGS:
            print(f"Business only allows 0-{BusinessTicket.MAX_CHECKED_BAGS} checked bags")
        self.__checked_bag_count = checked_bag_count

    checked_baggage_count = property(get_checked_bag_count, set_checked_bag_count)

    def calculate_price(self):
        paid_bags = max(0, self.__checked_bag_count - BusinessTicket._FREE_BAG_ALLOWANCE)
        price = self.get_base_fare() + paid_bags * BusinessTicket._BAG_FEE
        if self.__lounge_access:
            price += BusinessTicket._LOUNGE_FEE
        return price

    def baggage_allowance(self):
        return f'You have {self.__checked_bag_count} x 23 kg bags'

