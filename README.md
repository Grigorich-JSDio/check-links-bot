check-links-bot
===============
- Перед началом использования перейти на сайт [https://my.telegram.org/auth](https://my.telegram.org/auth "https://my.telegram.org/auth") и получить **api_id** и **api_hash**.
- Полученные данные занести в файл** .env **в корне
- Установка зависимостей командой **pip install -r requirements.txt**
- Запускать через app.py

------------
Для использования бота отправить ему любой файл с расширением **.txt**. Бот будет построчно проверять ссылки. Важно, чтобы в них не было **никаких лишних символов**, иначе ссылка будет считаться **невалидной**.
### Примеры ссылок:
- https://t.me/username
- http://t.me/username
- @username
- username
