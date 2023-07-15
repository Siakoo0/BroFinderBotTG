from enum import Enum

class UserRole(Enum):
    USER = 1
    ADMIN = 2
    BANNED = 3
    
class UserStatus(Enum):
    NORMAL = 1
    
    # CHAT
    CHAT = 2
    
    # SEARCH
    SEARCH = 3
    
    # GLOBAL MSG
    GLOBAL_MSG = 4
    GLOBAL_MSG_CONFIRM = 5
    GLOBAL_MSG_SEND = 6