# handlers/survey.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from states.survey import SurveyStates
from typing import Optional
from logger import logger

INTERESTS_QUESTION_MESSAGE = """
Напишите, что вам интересно — например: стрит-арт, история, кофейни, панорамы и т.д.
"""

TIME_QUESTION_MESSAGE = """
Сколько у вас времени на прогулку? Ответ укажите в минутах.
"""

ERROR_TIME_INPUT_QUESTION_MESSAGE = """
Сколько у вас времени на прогулку? Ответ укажите в минутах целым числом. Например, 60
"""

POSITION_QUESTION_MESSAGE = """
Отправь свой адрес или геопозицию — оттуда начнём маршрут!
"""

ERROR_WRONG_REQUEST_MESSAGE = """
Ваше сообщение не было корректно обработано. Пожалуйста, следуйте инструкциям.
"""

CONTINUE = "Продолжить"

SESSION_NOT_FOUND_MESSAGE = """
Сессия не найдена. Начните с /start.
"""

SEND_LOCATION_BUTTON_TEXT = """
Отправить моё местоположение
"""
router = Router()

#Старт-опроса-----------------------------------------------------------------------------------------#
@router.message(F.text == CONTINUE)
async def start_survey(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.interests)
    await message.answer(
        INTERESTS_QUESTION_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )

#Интересы-----------------------------------------------------------------------------------------#
@router.message(SurveyStates.interests)
async def handle_interests(message: Message, state: FSMContext):
    await state.update_data(interests=message.text.strip())
    logger.info(f"Пользователь {message.from_user.id} указал интересы: {message.text}")
    await state.set_state(SurveyStates.time)
    await message.answer(TIME_QUESTION_MESSAGE)

#Время-----------------------------------------------------------------------------------------#
@router.message(SurveyStates.time)
async def handle_time(message: Message, state: FSMContext):
    def validate_time(time : str) -> Optional[int]:
        try:
            minutes = int(time)
            if minutes >= 1 and minutes <= 1440:
                return minutes
        except Exception:
            return None
        
    user_id = message.from_user.id
    minutes = message.text.strip()
    logger.info(f"Пользователь {user_id} указал время: {message.text}")
    validated_time = validate_time(minutes)
    if not validated_time:
        logger.info(f"Указанное пользователем {user_id} время {message.text} не прошло валидацию.")
        await message.answer(ERROR_TIME_INPUT_QUESTION_MESSAGE)
        return
    
    logger.info(f"Указанное пользователем {user_id} время {message.text} прошло валидацию.")
    await state.update_data(time=minutes)
    await state.set_state(SurveyStates.location)
    markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=SEND_LOCATION_BUTTON_TEXT, request_location=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
    await message.answer(SEND_LOCATION_BUTTON_TEXT, reply_markup=markup)

#Местоположение-----------------------------------------------------------------------------------------#
#Не работает блин
@router.message(SurveyStates.location, F.location)
async def handle_location(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(location=f"{lat},{lon}")
    logger.info(f"Пользователь {user_id} ввел свое местоположение: широта {lat} долгота {lon}.")   

    data = await state.get_data()
    await message.answer(
        f"Спасибо! Ваши данные:\n"
        f"Интересы: {data['interests']}\n"
        f"Время: {data['time']} мин\n"
        f"Локация: {data['location']}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


#Для ввода текста вручную и для теста
@router.message(SurveyStates.location, F.text)
async def location_text_fallback(message: Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    data = await state.get_data()
    await message.answer(
        f"Спасибо! Ваши данные:\n"
        f"Интересы: {data['interests']}\n"
        f"Время: {data['time']} мин\n"
        f"Локация: {data['location']}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

#--------------------------------------------------------------------------------------------------#