import html
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.middlewares.localization import _
from bot.keyboards.reply import get_main_reply_keyboard
from bot.states.app_states import AppStates
from bot.services.gemini_service import GeminiService
from database.db_utils import increment_user_stat
from config import SUPPORTED_LANGUAGES, SUPPORTED_PROGRAMMING_LANGUAGES

common_router = Router()
gemini_service = GeminiService()


async def navigate_to_main_menu(message: Message, i18n: dict, state: FSMContext):
    await state.clear()
    await state.set_state(AppStates.idle)
    await message.answer(
        _('main_menu_text', i18n),
        reply_markup=get_main_reply_keyboard(i18n)
    )

@common_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    i18n = getattr(message.bot, 'i18n', {})
    await message.answer(_('welcome', i18n))
    await navigate_to_main_menu(message, i18n, state)

@common_router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    i18n = getattr(message.bot, 'i18n', {})
    await navigate_to_main_menu(message, i18n, state)

@common_router.message(F.text.in_([
    "⬅️ Back to Menu", "⬅️ В главное меню", "⬅️ Գլխավոր մենյու", "⬅️ Volver",
    "⬅️ Retour", "⬅️ Zurück zum Menü", "⬅️ Indietro", "⬅️ 返回",
    "⬅️ 戻る", "⬅️ 뒤로", "⬅️ वापस", "⬅️ Voltar", "⬅️ رجوع"
]))
async def handle_back_to_main_menu(message: Message, state: FSMContext):
    i18n = getattr(message.bot, 'i18n', {})
    await navigate_to_main_menu(message, i18n, state)

@common_router.message(Command("stats"))
async def cmd_stats(message: Message, user_db: dict):
    i18n = getattr(message.bot, 'i18n', {})
    streak = user_db.get('streak_count', 0)
    streak_text = _('streak_text', i18n, count=streak) if streak > 0 else ""

    await message.answer(
        _('stats_header', i18n) +
        _('stats_body', i18n,
          translations=user_db.get('translations_count', 0),
          concepts=user_db.get('words_learned_count', 0),
          quizzes=user_db.get('quizzes_passed_count', 0),
          facts=user_db.get('facts_requested_count', 0)
          ) + streak_text
    )

@common_router.message(Command("fact"))
async def cmd_fact(message: Message, user_db: dict):
    i18n = getattr(message.bot, 'i18n', {})
    processing_msg = await message.answer("🤔...")

    mode = user_db.get('learning_mode', 'human')
    interface_lang = SUPPORTED_LANGUAGES[user_db['interface_lang']]['gemini_name']

    if mode == 'human':
        subject = SUPPORTED_LANGUAGES[user_db['learning_lang']]['gemini_name']
    else:
        subject = SUPPORTED_PROGRAMMING_LANGUAGES[
            user_db['programming_lang']
        ]['display_name']

    fact = await gemini_service.get_fun_fact(mode, subject, interface_lang)

    await processing_msg.delete()
    if fact:
        await message.answer(_('fun_fact_text', i18n, subject=subject, fact=html.escape(fact)))
        await increment_user_stat(message.from_user.id, 'facts_requested_count')
    else:
        await message.answer(_('generation_error', i18n))