# api_id и api_hash: https://core.telegram.org/api/obtaining_api_id
api_id = 111111
api_hash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# id бота, который должен быть администратором в канале
# Также этот бот используется для управления ботом через телеграм
bot_token = '111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'  # (https://core.telegram.org/bots#6-botfather)

# Указывает на то, будут ли перенаправляться сообщения в канал (требуется установить telepot)
channel_enabled = True
# id канала. (https://github.com/GabrielRF/telegram-id#web-channel-id)
channel_id = -1111111111111
# Задержка между отправками сообщения в канал. -1 для мнгновенного, Inf для максимально больших сообщений
channel_delay = 3.5

# id или имя (@EchoBot) эхо-бота для получения уведомления. None, чтобы отключить
echo_id = '@EchoBot'

# Уведомлять ли не при помощи сторонних ботов, а при помощи своего бота. Отключает echo_id
notify_bot = True

# Указывает на то, будут ли приниматься команды управления (требуется установить telepot)
controller_enabled = True
# ID пользователя, который сможет управлять ботом. Ему же будут приходить уведомления, если notify_bot включен
admin_id = 11111111

# id бота с игрой (@RogBot)
bot_id = 253526115

# Для прокси требуется установить pysocks.
proxy_enabled = True  # Включить ли прокси
# Адрес этого прокси в формате {http,socks4,socks5}://[login:pass@]host:port, либо ссылка tg:// или {http,https}://t.me/
proxy = 'https://t.me/socks?server=example.com&port=1234&user=username&pass=password'

test = False  # Будет принимать сообщения не из телеграма, а слушать порт
test_host = '127.0.0.1'
test_port = 12345

# Проценты -- число от 0 до 1
hp_heal = 0.95  # Со скольки процентов здоровья следует лечиться у Аллаха
hp_battle = 0.75  # Со скольки процентов здоровья надо внезапно начинать битву
hp_stop = 0.5  # Со скольки процентов здоровья надо остановиться.
battle_count = 30  # Со скольки заходов в одну и ту же комнату надо начинать битву
timeout = 2  # Сколько бот будет ждать сообщение
update_delay = 0.2  # Задержка в секундах между получения информации о новых сообщениях
message_delay = 2  # Задержка в секундах перед отправкой сообщения
retry_delay = 20  # Задержка между повторными отправками сообщения
crash_delay = 5  # Задержка после падения бота
pause_delay = 60  # Задержка в случае очень низкого hp (stop)
