from typing import Any

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router(name=__name__)


@start_router.message(CommandStart())
async def send_start_message(message: Message) -> Any:
    await message.answer("Привет!")
