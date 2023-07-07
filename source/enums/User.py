from enum import Enum

class UserRole(Enum):
    USER = 1
    ADMIN = 2
    
class UserStatus(Enum):
    NORMAL = 1
    CHAT = 2
    SEARCH = 3