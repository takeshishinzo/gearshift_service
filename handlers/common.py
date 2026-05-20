from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.inline import book_start_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Welcome to <b>GearShift Auto</b>! 🛠️\nYour trusted car care partner.",
        parse_mode="HTML",
        reply_markup=book_start_kb(),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    await state.clear()
    if current:
        await message.answer("❌ Booking cancelled.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Nothing to cancel. Use /start to begin.")
