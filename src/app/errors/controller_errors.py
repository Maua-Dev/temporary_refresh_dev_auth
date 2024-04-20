from .base_error import BaseError

class MissingParameter(BaseError):
    def __init__(self, param: str):
        super().__init__(f'Field {param} is required')