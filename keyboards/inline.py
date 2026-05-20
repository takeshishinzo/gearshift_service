from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

SERVICES: list[tuple[str, str]] = [
    ("🔧 Oil Change",   "oil_change"),
    ("🛑 Brake Repair", "brake_repair"),
    ("🔍 Diagnostics",  "diagnostics"),
    ("🔩 Other Repair", "other_repair"),
]

SLOTS: list[tuple[str, str]] = [
    ("Mon 10:00 AM", "mon_10am"),
    ("Mon 02:00 PM", "mon_2pm"),
    ("Tue 11:00 AM", "tue_11am"),
    ("Tue 03:00 PM", "tue_3pm"),
    ("Wed 09:00 AM", "wed_9am"),
]


def services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, data in SERVICES:
        builder.button(text=label, callback_data=f"svc:{data}")
    builder.adjust(2)
    return builder.as_markup()


def slots_kb(taken: set[str]) -> InlineKeyboardMarkup:
    """Build time-slot keyboard, marking taken slots as unavailable."""
    builder = InlineKeyboardBuilder()
    for label, data in SLOTS:
        if data in taken:
            builder.button(text=f"❌ {label}", callback_data="slot:taken")
        else:
            builder.button(text=label, callback_data=f"slot:{data}")
    builder.adjust(2)
    return builder.as_markup()


def book_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Book a Service", callback_data="book:start")]
    ])


def contact_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Share Contact Number", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
