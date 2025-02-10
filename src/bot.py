import asyncio
import datetime

from telethon import TelegramClient, events, Button

from db.database import DataBase
from metrics import Scorer

# Create a TelegramClient instance
db = DataBase()
bot = TelegramClient('bot_session', **db.config['credentials']).start(bot_token=db.config['bot_token'])
scr = Scorer('resources/sasha.csv')


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = sender.id
    db.add_user(user_id)
    await event.reply(
        """Соберём ваши опечатки и посчитаем ваш скор отклонения от стандартного русского языка.
/pair --- добавить пару
/score --- посчитать скор (max. 100)
/history --- посмотреть все пары, которые вы записали"""
    )


@bot.on(events.NewMessage(pattern='/score'))
async def history(event):
    sender = await event.get_sender()
    user_id = sender.id

    pairs = db.select_pairs(user_id)
    print(pairs)

    if pairs:
        score = scr.get_score(pairs)
        reply = f"Ваш скор: {score}"  # TODO: add score calculation
        await event.reply(reply)
    else:
        await event.reply("Нет пар для подсчёта скора.")


@bot.on(events.NewMessage(pattern='/history'))
async def history(event):
    sender = await event.get_sender()
    user_id = sender.id

    pairs = db.select_pairs(user_id)

    if pairs:
        await event.reply(f"Ваши пары, всего {len(pairs)}:")
        pairs_reply = '\n'.join([f"{obj.written} вместо {obj.intended}" for obj in pairs])
        await event.reply(pairs_reply)
    else:
        await event.reply("Вы пока не записали ни одной пары.")


@bot.on(events.NewMessage(pattern='/pair'))
async def pair_handler(event):
    sender = await event.get_sender()
    async with bot.conversation(sender) as conv:
        # Ask the user for the word
        await conv.send_message("Введите пару через ' - ', например: 'пакля - рвакля'")

        # Wait for the user's response
        response = await conv.get_response()
        inp = response.text.strip()
        if len(inp) < 2:
            await conv.send_message(
                "Пожалуйста, напишите пару через ' - ', например: 'пакля - рвакля'. Попробуйте ещё раз: /pair")
            return

        written, intended = inp.split(' - ')

        # Ask for confirmation with keyboard
        keyboard = [
            [Button.inline("Да", data="yes"),
             Button.inline("Нет", data="no")]
        ]
        await conv.send_message(f"Вы написали '{written}' вместо '{intended}', всё так?", buttons=keyboard)

        # Wait for the user's confirmation
        confirmation = await conv.wait_event(events.CallbackQuery())

        # Process the confirmation
        if confirmation.data == b"yes":
            # Log the word (in this example, we're just printing it)
            print(f"Сохранили пару: '{written}' вместо '{intended}'")
            db.add_pairs(written, intended, datetime.datetime.now(), sender.id)
            await conv.send_message(f"Сохранили пару: '{written}' вместо '{intended}'")
        elif confirmation.data == b"no":
            await conv.send_message("Хорошо, не сохраняем. Сохранить другую пару: /pair")
        else:
            await conv.send_message("Что-то пошло не так...")

        await conv.send_message("Сохранить другую пару: /pair")


async def main():
    await bot.run_until_disconnected()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
