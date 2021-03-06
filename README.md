# RogueBotBot
## Установка  
Бот работает на Python >= 3.5.  
Для работы бота требуется [`telethon`](https://github.com/LonamiWebs/Telethon). Но для дополнительных функций, таких как управление через телеграм и перенаправлание сообщений в телеграм, нужно установить [`telepot`](https://github.com/nickoala/telepot/). Для работы прокси дополнительно нужен [`PySocks`](https://github.com/Anorov/PySocks).  
Итого, желательно установить всё одной командой: `pip install telethon telepot PySocks`  
  
## Настройка  
Все файлы настроек находятся в каталоге `Bot/Configurable/`  
Все основные параметры бота хранятся в файле `Config.py`  
Бот умеет покупать предметы в необходимом количестве.  
Настройки покупок находятся в `BuyItems.py`.  
Бот использует указатель и выбирает наиболее желательную комнату; приоритеты комнат находятся в `RoomsPriority.py`.  
При запуске продажи используются параметры из `SellItems.py`  
Способы прохождения комнат хранятся в `Rooms.py`  
  
## Запуск  
Запускается бот при помощи файла `main.py`.  
Есть следующие аргументы:  
* `--game` (`-g`): запускает игру. Может потребоваться вручную отправить одно сообщение  
* `--inventory` (`-i`): сканирует игровой инвентарь  
* `--sell` (`-s`): продает предметы согласно настройкам в `SellItems.py`  
* `--check PATH_TO_REPO`: проверяет, не изменились ли комнаты. `PATH_TO_REPO` -- путь к [коду игры](https://github.com/yegorf1/RogueBot)  
  
**Внимание! Бот расчитан на прокачанных персонажей!**
*Рекомендую подкорректировать комнату "Горшок золота", если не можете справиться с Леприконом и прокачать харизму для быстрой победой над зеркалом*
