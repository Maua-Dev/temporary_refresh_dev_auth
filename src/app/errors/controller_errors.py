from .base_error import BaseError

class MissingParameters(BaseError):
    def __init__(self, param: str):
        super().__init__(f'Field {param} is required')
        
class WrongTypeParameters(BaseError):
    def __init__(self, field_name: str, field_type_expected: str, field_type_received):
        super().__init__(f'Field {field_name} isn\'t in the right type.\n Received: {field_type_expected}.\n Expected: {field_type_received}')
        
        
class Forbidden(BaseError):
    def __init__(self):
        super().__init__(f'You don\'t have permission to access this resource')