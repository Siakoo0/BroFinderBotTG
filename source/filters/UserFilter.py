from pyrogram import filters

from source.enums.User import UserStatus, UserRole

from source.models.User import User

def status(status : UserStatus):
    async def func(flt, __, update):
        user = User.get_or_none((User.id == update.from_user.id) & (User.status == flt.status.value))
        return user is not None
        
    return filters.create(func, status=status)

def role(role : UserRole):
    async def func(flt, __, update):
        user = User.get_or_none((User.id == update.from_user.id) & (User.role == flt.role.value))
        return user is not None
        
    return filters.create(func, role=role)