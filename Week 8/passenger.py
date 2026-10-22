class Passenger():
    def __init__(self, name, email, passport_number):
        self.__name = name
        self.__email = email
        self.__passport_number = passport_number

    def get_name(self):
        return self.__name

    def set_name(self, name):
        if isinstance(name, str):
            self.__name = name

    name = property(get_name, set_name)

    def get_email(self):
        return self.__email

    def set_email(self, email):
        if isinstance(email, str):
            self.__email = email

    email = property(get_email, set_email)

    def get_passport_number(self):
        return self.__passport_number

    def set_passport_number(self, passport_number):
        if isinstance(passport_number, str):
            self.__passport_number = passport_number

    passport_number = property(get_passport_number, set_passport_number)


    def equals(self, other):
        if not isinstance(other, Passenger):
            return False
        return self.__passport_number == other.get_passport_number()