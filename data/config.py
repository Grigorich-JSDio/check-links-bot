from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
api_id = env.int('api_id')
api_hash = env.str('api_hash')
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов


