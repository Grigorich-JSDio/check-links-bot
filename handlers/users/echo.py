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
            if re.match('http[s]{0,1}://t.me/[a-z]{1,}[a-z0-9_]{4,31}$', line.lower()) or re.match(
                    '@{0,1}[a-z]{1,}[a-z0-9_]{4,31}$', line.lower()) or re.match(
                    r'http[s]{0,1}://t.me/joinchat/[0-9a-z\-_]{1}[a-z_\-0-9]{4,}$', line.lower()):
                links.append(line.replace('\n', ''))
    if len(links) == 0:
        return 'error', 'В вашем файле нет ни одной ссылки'
    else:
        return 'success', f'В вашем файле {len(links)} ссылок. Для минимизации возможности получения флуда работает ограничение: 1 ссылка - 1 секунда', links


async def check_link(links):
    async with TelegramClient('anon', api_id, api_hash) as client:
        badlinks = []
        active_links = []
        end_status = 'success'
        end_mess = 'Операция завершена успешно. Высылаем файл с результатами.'
        for x in links:
            try:
                if re.match(privlink_pattern, x.lower()):
                    hash = x.rsplit('/', 1)[1]
                    try:
                        ch = await client(CheckChatInviteRequest(hash))
                        active_links.append(x)
                    except errors.InviteHashEmptyError:
                        badlinks.append(x)
                        continue
                    except errors.InviteHashExpiredError:
                        badlinks.append(x)
                        continue
                    except errors.InviteHashInvalidError:
                        badlinks.append(x)
                        continue
                else:
                    try:
                        ch = await client.get_entity(x)
                        active_links.append(x)
                    except errors.UsernameInvalidError:
                        badlinks.append(x)
                        continue
                    except:
                        badlinks.append(x)
                time.sleep(1)
            except telethon.errors.FloodError as e:
                end_status = 'flood_error'
                end_mess = f'К сожалению, на ваш аккаунт наложено временное ограничение в {e.seconds} секунд. Высылаем вам обработанные результаты.'
                break
            except ValueError:
                continue
        filenames = []
        time_now = datetime.datetime.now().strftime("%d-%m-%y %H_%M_%S")
        if len(badlinks) > 0:
            filename = f'Неактив {time_now}.txt'
            with open(filename, 'w+') as f:
                for link in badlinks:
                    f.write(f'{link}\n')
            filenames.append(filename)
        if len(active_links) > 0:
            filename = f'Актив {time_now}.txt'
            with open(filename, 'w+') as f:
                for link in active_links:
                    f.write(f'{link}\n')
            filenames.append(filename)
        if len(filenames) != 0:
            return end_status, end_mess, filenames
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
                for x in res[2]:
                    await message.answer_document(types.InputFile(x, filename=x))
