import logging
import sys
import Bot

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler("RogBotBot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ])

    Bot.Bot.main()
