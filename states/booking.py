from aiogram.fsm.state import State, StatesGroup


class Booking(StatesGroup):
    service  = State()
    vehicle  = State()
    slot     = State()
    contact  = State()
