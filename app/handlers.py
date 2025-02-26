from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import pandas as pd
import re
import app.keyboards as kb

router = Router()

def CountPeopleInGroup(df, group_prefix, Name):
    count = 0
    found_group = False
    for value in df[Name]:
        if not found_group:
            if str(value).startswith(group_prefix):
                found_group = True
                count += 1
        else:
            if str(value)[0].isdigit():
                break
            count += 1
    return count - 1 if found_group else 0

VariableGroups = [str(i) + j for i in range(1, 22) for j in 'АБВГДЕС']

def MoneyCounter(GroupNumbers, NumberOfShifts):
    allMoney = 0
    allPersons = 0
    report = "📊 Отчет по зарплате:\n\n"  # Заголовок отчета
    for group in GroupNumbers:
        group = group.upper()
        if group[-1] == '+' and group[:-1] in VariableGroups:
            group = group[:-1]
            number = int(''.join(re.findall(r'\d', group)))
            if number <= 2:
                literal = re.sub(r'[^a-zA-Zа-яА-Я]', '', group)
                url = f"https://docs.google.com/spreadsheets/d/1Lmb9z1rLv0N6CwEOtjXC4rq5qjOlDWLWLPQHyT7if2w/export?format=csv&gid={sheets_id1[number - 1]}"
                try:
                    df_google = pd.read_csv(url)
                    df_cleaned = df_google.dropna(subset=['Полугодовой курс'])
                    persons = CountPeopleInGroup(df_cleaned, group, 'Полугодовой курс')
                    allPersons += persons
                    money = 0
                    if literal in 'АБВГ':
                        money = money + (persons * 330)
                    elif literal in 'ДЕ':
                        money = money + (persons * 175)
                    elif literal in 'С':
                        money = money + (persons * 100)
                    if persons:
                        report += f"🔹 Группа '{group}+': {persons} человек.\n"
                        report += f"💰 Деньги за группу: {money} рублей.\n\n"
                    else:
                        report += f"🔹 Группа '{group}+' пустая -> 0 рублей.\n\n"
                    allMoney += money
                except Exception as e:
                    report += f"❌ Ошибка при обработке группы '{group}+': {e}\n\n"
        elif group in VariableGroups:
            number = int(''.join(re.findall(r'\d', group)))
            literal = re.sub(r'[^a-zA-Zа-яА-Я]', '', group)
            url = f"https://docs.google.com/spreadsheets/d/1Lmb9z1rLv0N6CwEOtjXC4rq5qjOlDWLWLPQHyT7if2w/export?format=csv&gid={sheets_id[number-1]}"
            try:
                df_google = pd.read_csv(url)
                df_cleaned = df_google.dropna(subset=['Имя из базы'])
                persons = CountPeopleInGroup(df_cleaned, group, 'Имя из базы')
                allPersons += persons
                money = 0
                if literal in 'АБВГ':
                    money = money + (persons * 330)
                elif literal in 'ДЕ':
                    money = money + (persons * 175)
                elif literal in 'С':
                    money = money + (persons * 100)
                if persons:
                    report += f"🔹 Группа '{group}': {persons} человек.\n"
                    report += f"💰 Деньги за группу: {money} рублей.\n\n"
                else:
                    report += f"🔹 Группа '{group}' пустая -> 0 рублей.\n\n"
                allMoney += money
            except Exception as e:
                report += f"❌ Ошибка при обработке группы '{group}': {e}\n\n"
        else:
            report += f"❌ Группы '{group}' не существует.\n\n"
    report += f"👥 Учеников всего: {allPersons}\n\n"
    if NumberOfShifts:
        report += f"👨‍💻 За дежурства: {NumberOfShifts * 250} рублей.\n\n"
    allMoney += NumberOfShifts * 250
    report += f"✅ Всего заработано: {allMoney} рублей.\n"
    report += f'💸С учётом налогового вычета 4% заработано: {round(allMoney*0.96, ndigits=1)} рублей.\n'
    report += f'😡Государство украло у тебя {round(allMoney*0.04,ndigits=1)} рублей.'
    return report

sheets_id = ['1177914284', '1582062197', '1813299202','1669253695','1092321537','537534507','586781294','639277697','426873248','974436486','1851753723',
             '821446178','685908788','2094433417','680377502','1895774609','1081909124','1151250149','1099529776','1486463467','1491617643']
sheets_id1 = ['1297736012','1382954324']

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}👋\nЭто бот, который поможет подсчитать зарплату🤑', reply_markup=kb.main)

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Чтобы узнать зарплату за этот месяц, введи название групп через пробел в формате (1А 2б+ 0)')

@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('')
    await callback.message.edit_text(f'Привет, {callback.from_user.first_name}👋\nЭто бот, который поможет подсчитать зарплату🤑', reply_markup=kb.main)


class Form(StatesGroup):
    waiting_for_groups = State()

@router.callback_query(F.data == 'begin')
async def begin(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(
        'Чтобы узнать зарплату за этот месяц, введи название групп через пробел в формате (1А 2б+ 0)',
        reply_markup=kb.buttons
    )
    await state.set_state(Form.waiting_for_groups)

@router.message(Form.waiting_for_groups)
async def process_groups(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Пожалуйста, введите группы и количество дежурств через пробел в формате: 1А 2б 0")
            return
        
        GroupNumbers = parts[:-1]
        try:
            NumberOfShifts = int(parts[-1])
        except ValueError:
            await message.answer("❌ Количество дежурств должно быть числом.")
            return

        report = MoneyCounter(GroupNumbers, NumberOfShifts)
        await message.answer(report, reply_markup=kb.buttons)
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {e}. Проверьте ввод и попробуйте снова.")

@router.message()
async def random_message(message: Message):
    await message.answer("Начните☝️")
