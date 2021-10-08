import telethon
import xlwt
from aiogram import types
from aiogram.dispatcher import FSMContext
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon import errors
import asyncio
import datetime
import re
import time
from loader import dp
from data.config import api_id, api_hash
from telethon.sync import TelegramClient, events


privlink_pattern = r'http[s]{0,1}://t.me/joinchat/[0-9a-z\-_]{1}[a-z_\-0-9]{4,}$'


def get_links():
    links = []
    with open('links.txt', encoding='UTF-8') as f:
        for line in f:
            if re.match('http[s]{0,1}://t.me/[a-z]{1,}[a-z0-9_]{4,31}$', line) or re.match(
                    '@{0,1}[a-z]{1,}[a-z0-9_]{4,31}$', line.lower()) or re.match(
                    r'http[s]{0,1}://t.me/joinchat/[0-9a-z\-_]{1}[a-z_\-0-9]{4,}$', line.lower()):
                links.append(line.replace('\n', ''))
    if len(links) == 0:
        return 'error', 'В вашем файле нет ни одной ссылки'
    else:
        return 'success', f'В вашем файле {len(links)} ссылок. Для минимизации возможности получения флуда работает ограничение: 1 ссылка - 1 секунда', links


async def check_link(links):
    async with TelegramClient('anon', api_id, api_hash) as client:
        users = []
        channels = []
        chats = []
        priv_chats = []
        end_status = 'success'
        end_mess = 'Операция завершена успешно. Высылаем файл с результатами.'
        for x in links:
            try:
                if re.match(privlink_pattern, x.lower()):
                    hash = x.rsplit('/', 1)[1]
                    try:
                        ch = await client(CheckChatInviteRequest(hash))
                        if ch.__class__.__name__ == 'ChatInviteAlready':
                            if ch.chat.__class__.__name__ == 'Channel':
                                if ch.chat.megagroup is True:
                                    chats.append({'id': ch.chat.id, 'url': x, 'title': ch.chat.title})
                                else:
                                    channels.append({'id': ch.chat.id, 'url': ch.chat.username, 'title': ch.chat.title})
                        elif ch.__class__.__name__ == 'ChatInvite':
                            if ch.megagroup is True:
                                priv_chats.append({'hash': hash, 'url': x, 'title': ch.title})
                            else:
                                continue
                    except errors.InviteHashEmptyError or errors.InviteHashExpiredError or \
                        errors.InviteHashInvalidError:
                        continue
                else:
                    ch = await client.get_entity(x)
                if ch.__class__.__name__ == 'Channel':
                    if ch.megagroup is True:
                        chats.append({'id': ch.id, 'url': ch.username, 'title': ch.title})
                    else:
                        channels.append({'id': ch.id, 'url': ch.username, 'title': ch.title})
                elif ch.__class__.__name__ == 'User':
                    name = ch.first_name
                    if ch.last_name is not None:
                        name = f'{name} {ch.last_name}'
                    users.append({'id': ch.id, 'username': ch.username, 'full_name': name})
                time.sleep(1)
            except telethon.errors.FloodError as e:
                end_status = 'flood_error'
                end_mess = f'К сожалению, на ваш аккаунт наложено временное ограничение в {e.seconds} секунд. Высылаем вам обработанные результаты.'
                break
            except ValueError:
                continue
            wb = xlwt.Workbook()
            total_lists = 0
            if len(users) > 0:
                total_lists += 1
                sheet = wb.add_sheet(f'Users')
                sheet.write(0, 0, 'User ID')
                sheet.write(0, 1, 'Username')
                sheet.write(0, 2, 'Full Name')
                n = 1
                for q in range(len(users)):
                    sheet.write(n, 0, users[q]['id'])
                    sheet.write(n, 1, users[q]['username'])
                    sheet.write(n, 2, users[q]['full_name'])
                    n += 1
            if len(channels) > 0:
                total_lists += 1
                sheet = wb.add_sheet(f'Channels')
                sheet.write(0, 0, 'Channel ID')
                sheet.write(0, 1, 'URL')
                sheet.write(0, 2, 'Title')
                n = 1
                for q in range(len(channels)):
                    sheet.write(n, 0, channels[q]['id'])
                    sheet.write(n, 1, channels[q]['url'])
                    sheet.write(n, 2, channels[q]['title'])
                    n += 1
            if len(chats) > 0:
                total_lists += 1
                sheet = wb.add_sheet(f'Chats')
                sheet.write(0, 0, 'Chat ID')
                sheet.write(0, 1, 'URL')
                sheet.write(0, 2, 'Title')
                n = 1
                for q in range(len(chats)):
                    sheet.write(n, 0, chats[q]['id'])
                    sheet.write(n, 1, chats[q]['url'])
                    sheet.write(n, 2, chats[q]['title'])
                    n += 1
            if len(priv_chats) > 0:
                total_lists += 1
                sheet = wb.add_sheet(f'Private Chats')
                sheet.write(0, 0, 'Hash')
                sheet.write(0, 1, 'URL')
                sheet.write(0, 2, 'Title')
                n = 1
                for q in range(len(priv_chats)):
                    sheet.write(n, 0, priv_chats[q]['hash'])
                    sheet.write(n, 1, priv_chats[q]['url'])
                    sheet.write(n, 2, priv_chats[q]['title'])
                    n += 1
        time_now = datetime.datetime.now().strftime("%d-%m-%y %H_%M_%S")
        filename = f'Результаты {time_now}.xls'
        wb.save(filename)
        if total_lists != 0:
            return end_status, end_mess, filename
        else:
            return 'links_error', 'В вашем файле не было ни одной рабочей ссылки'



@dp.message_handler()
async def bot_echo(message: types.Message):
    await message.answer(f"Я принимаю только `.txt` файлы!", parse_mode='Markdown')


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def bot_echo(message: types.Message):
    if message.document.mime_type != "text/plain":
        await message.answer(f"Я принимаю только `.txt` файлы!", parse_mode='Markdown')
    else:
        await message.answer(f"Начинаю обработку...")
        await message.document.download(destination='links.txt')
        links = get_links()
        if links[0] == 'error':
            await message.answer(links[1])
        else:
            await message.answer(links[1])
            res = await (check_link(links[2]))
            if res[0] == 'links_error':
                await message.answer(res[1])
            else:
                await message.answer(res[1])
                await message.answer_document(types.InputFile(res[2], filename=res[2]))
