from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from database import requests, db_core
from keyboards.inline import SERVICES, SLOTS, services_kb, slots_kb, contact_kb
from states.booking import Booking

router = Router()

# Label lookup maps built once at import time
_SVC_LABELS  = {data: label for label, data in SERVICES}
_SLOT_LABELS = {data: label for label, data in SLOTS}


@router.callback_query(F.data == "book:start")
async def booking_start(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text("🔧 <b>Step 1/4</b> — Select a service:", parse_mode="HTML", reply_markup=services_kb())
    await state.set_state(Booking.service)
    await call.answer()



@router.callback_query(Booking.service, F.data.startswith("svc:"))
async def service_chosen(call: CallbackQuery, state: FSMContext) -> None:
    service_key = call.data.split(":", 1)[1]
    await state.update_data(service=service_key)
    await call.message.edit_text(
        "🚗 <b>Step 2/4</b> — Enter your vehicle details:\n"
        "<i>Make, Model, Year — e.g. Toyota Camry 2021</i>",
        parse_mode="HTML",
    )
    await state.set_state(Booking.vehicle)
    await call.answer()



@router.message(Booking.vehicle, F.text)
async def vehicle_entered(message: Message, state: FSMContext) -> None:
    await state.update_data(vehicle=message.text.strip())

    # Fetch already-taken slots to mark them
    taken: set[str] = set()
    for _, slot_key in SLOTS:
        if await requests.is_slot_taken(db_core.db_pool, slot_key):
            taken.add(slot_key)

    await message.answer(
        "🕐 <b>Step 3/4</b> — Choose an available time slot:",
        parse_mode="HTML",
        reply_markup=slots_kb(taken),
    )
    await state.set_state(Booking.slot)



@router.callback_query(Booking.slot, F.data == "slot:taken")
async def slot_taken(call: CallbackQuery) -> None:
    await call.answer("⚠️ This slot is already booked. Please choose another.", show_alert=True)


@router.callback_query(Booking.slot, F.data.startswith("slot:"))
async def slot_chosen(call: CallbackQuery, state: FSMContext) -> None:
    slot_key = call.data.split(":", 1)[1]
    await state.update_data(slot=slot_key)
    await call.message.edit_text(
        "📱 <b>Step 4/4</b> — Please share your contact number:",
        parse_mode="HTML",
        reply_markup=None,
    )
    await call.message.answer("Tap the button below 👇", reply_markup=contact_kb())
    await state.set_state(Booking.contact)
    await call.answer()



@router.message(Booking.contact, F.contact)
async def contact_received(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    data  = await state.get_data()
    await state.clear()

    user = message.from_user
    service_key = data["service"]
    slot_key    = data["slot"]
    vehicle     = data["vehicle"]

    # Persist to database
    await requests.upsert_user(db_core.db_pool, user.id, user.username, user.full_name, phone)
    car_id = await requests.insert_car(db_core.db_pool, user.id, vehicle)
    appt_id = await requests.insert_appointment(db_core.db_pool, user.id, car_id, service_key, slot_key)

    service_label = _SVC_LABELS.get(service_key, service_key)
    slot_label    = _SLOT_LABELS.get(slot_key, slot_key)

    await message.answer(
        f"✅ <b>Booking Confirmed!</b> (#{appt_id})\n\n"
        f"🔧 <b>Service:</b> {service_label}\n"
        f"🚗 <b>Vehicle:</b> {vehicle}\n"
        f"🕐 <b>Slot:</b> {slot_label}\n"
        f"📱 <b>Phone:</b> {phone}\n\n"
        "We'll see you soon at <b>GearShift Auto</b>! 🛠️",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
