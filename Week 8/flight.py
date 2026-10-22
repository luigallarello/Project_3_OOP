
MAX_FUEL_LEVEL = 100


class Plane():
    def __init__(self, tail_number, model, capacity, fuel_level, status):
        self.__tail_number = tail_number
        self.__model = model
        self.__capacity = capacity
        self.__fuel_level = fuel_level
        self.__status = status

    def get_tail_number(self):
        return self.__tail_number

    def set_tail_number(self, tail_number):
        if isinstance(tail_number, str):
            self.__tail_number = tail_number
        else: 
            print('Please assign a proper tail number.')

    tail_number = property(get_tail_number, set_tail_number)


    def get_model(self):
        return self.__model

    def set_model(self, model):
        if isinstance(model, str):
            self.__model = model
        else:
            print('Invalid plane model')

    model = property(get_model, set_model)


    def get_capacity(self):
        return self.__capacity
    
    def set_capacity(self, capacity):
        if isinstance(capacity, str):
            self.__capacity = capacity
        else:
            print('Invalid capacity type')
    
    capacity = property(get_capacity, set_capacity)


    def get_fuel_level(self):
        return self.__fuel_level
        
    def set_fuel_level(self, fuel_level):
        if isinstance(fuel_level, int):
            if fuel_level + self.__fuel_level <= MAX_FUEL_LEVEL:
                self.__fuel_level = fuel_level
            elif fuel_level + self.__fuel_level >= MAX_FUEL_LEVEL:
                print('Too much fuel, try adding less.')
        
    fuel_level = property(get_fuel_level, set_fuel_level)


    def get_status(self):
        return self.__status
    
    def set_status(self, status):
        if isinstance(status, str):
            
               
        
    status = property(get_fuel_level, set_fuel_level)

    def refuel(self, amount):
        if isinstance(amount, int):
            if amount + self.__fuel_level <= MAX_FUEL_LEVEL:
                self.__fuel_level += amount
                print(f'{amount} fuel level added to the tank.')
            elif amount + self.__fuel_level >= MAX_FUEL_LEVEL:
                print('Too much fuel, try adding less.')
        else:
            'Not a valid fuel type'
        return self.__fuel_level

    def update_status(self, new_status):
        if isinstance(new_status, str):
            if new_status == 'Idle':
                self.__status = 'Idle'
            elif