from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

main = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text='Начать', callback_data='begin')]
])

buttons = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])
