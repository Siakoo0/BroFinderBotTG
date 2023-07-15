from source.handlers.abs_handlers.Common import Common

from source.filters.UserFilter import role
from source.enums.User import UserRole


class AdminHandler(Common): 
    def filters(self):
        return role(UserRole.ADMIN)