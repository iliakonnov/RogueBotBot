import argparse
import json
import logging
import os
from time import time, sleep

from Bot import BotState, ReplyFunc, telegrammer, controller, Controller, utils, Config, BuyItems, Rooms, Actions, \
    ReplyUtils, SellItems, Constants, RoomsPriority, Room, notifier, logger, channel


def bot(state: BotState):
    last_time = time()
    action: ReplyFunc = None
    message = None

    work = True
    paused_hp = False
    paused = False
    use_sign = False
    old_room = None
    while work:
        try:
            commands = controller.get_commands()
            for i in commands:
                if i == Controller.Command.UNPAUSE:
                    paused = False
                elif i == Controller.Command.PAUSE:
                    paused = True
                elif i == Controller.Command.INVENTORY:
                    state.current_items = load_inventory()
            channel.send_to_channel(message=None)
            if paused:
                continue

            old_room = state.current_room
            temp_message = telegrammer.get_message(timeout=Config.timeout)

            if not temp_message:
                if time() - last_time > Config.retry_delay:
                    logging.warning('Retrying last message...')
                    if state.current_retries_count == 1:
                        logging.warning(ReplyUtils.get_info(action))
                    state.current_retries_count += 1
                else:
                    continue
            else:
                message = temp_message
                state.current_retries_count = 0

                logging.debug('Received message: ' + message.text.replace('\n', '\\n'))
                action = None

                state.damage = utils.try_find(Constants.damage_re, message.text, post=int, default=state.damage)
                state.health = utils.try_find(Constants.hp_gold_re, message.text, group=1, post=int, default=state.health)
                state.dice = utils.try_find(Constants.dice_re, message.text, group=1, post=int, default=state.dice)
                state.max_hp = max(state.health, state.max_hp)

                state.gold = utils.try_find(Constants.hp_gold_re, message.text, group=2, post=int, default=state.gold)

                use_sign = False

                if state.health <= state.max_hp * Config.hp_stop:
                    if not paused_hp:
                        logging.error('Very low health. Pause bot!')
                        notifier.notify("Very low hp!")("", [], state)
                        paused_hp = True
                    sleep(Config.pause_delay)
                    continue
                elif paused_hp:
                    logging.info('All good. Continuing')
                    paused_hp = False
                if 'Что будем делать?' in message.text:  # TODO: Перенести эти if'ы в Actions, если возможно
                    state.current_room_count = 0
                    new_item = utils.try_find(Constants.item_re, message.text)
                    if new_item is not None and new_item != 'Ничего.':
                        if new_item not in state.current_items:
                            state.current_items[new_item] = 0
                            state.current_items[new_item] += 1

                    if state.health < state.max_hp * Config.hp_heal and '🙏 Молить Бога о выходе' in message.replies:
                        action = ReplyUtils.concat(action,
                                                   ReplyUtils.reply('🙏 Молить Бога о выходе'),
                                                   ReplyUtils.reply('Аллах'))
                        state.current_room = '__бог->коридор'
                    if state.current_room != '__алхимик' and '🛍 Зайти в Магазин алхимика' in message.replies:
                        action = ReplyUtils.concat(action, ReplyUtils.reply('🛍 Зайти в Магазин алхимика'))
                        state.current_room = '__алхимик'
                    else:
                        use_sign = True
                elif state.current_room == '__алхимик' or \
                        'Привет! Давно не виделись, смотри, что у меня есть' in message.text or \
                        'У меня такого нет' in message.text:
                    found = False
                    for key, value in BuyItems.items.items():
                        if found:
                            continue
                        if key in message.replies and state.current_items[key] < value:
                            found = True
                            state.current_items[key] += 1
                            action = ReplyUtils.concat(action, ReplyUtils.reply(key))
                    if not found:
                        action = ReplyUtils.concat(action, ReplyUtils.reply('Выход'))
                    state.current_room = '__коридор'
                    use_sign = True
                elif '🎲 Не вижу уверенности!' in message.text:
                    action = ReplyUtils.concat(action, ReplyUtils.dice)
                else:
                    if state.health <= state.max_hp * Config.hp_battle:
                        logging.warning('Low health, starting battle!')
                        action = ReplyUtils.concat(action, ReplyUtils.battle)
                    elif state.current_room_count > Config.battle_count:
                        logging.warning('Too long in room, starting battle!')
                        action = ReplyUtils.concat(action, ReplyUtils.battle)
                    else:
                        room = utils.try_find(Constants.room_re, message.text)
                        if room is None:
                            room = state.current_room
                        else:
                            state.current_room = room
                        if room == 'Распутье':
                            found = False
                            for n in RoomsPriority.rooms:
                                if n in message.replies and not found:
                                    action = ReplyUtils.concat(action, ReplyUtils.reply(n))
                                    state.current_room = n
                                    state.current_room_count = 0
                                    state.rooms_entered += 1
                                    found = True
                        else:
                            found = False
                            for r in Rooms.rooms:
                                if r.check_name(room):
                                    action = ReplyUtils.concat(action, r.action)
                                    state.current_room_count += 1
                                    found = True
                            if not found:
                                logging.warning('Unknown room: ' + repr(room))
            # endif (not message).

            new_action = ReplyUtils.concat(action, *Actions.actions, ignore_func=None)

            if use_sign:
                new_action = ReplyUtils.concat(
                    new_action,
                    ReplyUtils.concat(
                        ReplyUtils.reply('Использовать Указатель'),
                        ReplyUtils.update_state('current_room', 'Распутье'),
                        ignore_func=None
                    )
                )

            print('Sending: ' + ReplyUtils.get_info(new_action))
            last_time = ReplyUtils.send_action(new_action, message, state)
            logging.info(
                'Room: {} -> {}; HP: {}; dmg: {}; gold: {}; dice: {}'.format(
                    old_room, state.current_room, state.health, state.damage, state.gold, state.dice))
            sleep(Config.update_delay)
        except KeyboardInterrupt:
            work = False
        except Exception:
            logging.exception('Exception occurred!')
            state.crashes += 1
            sleep(Config.crash_delay)
        with open('bot_state.json', 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=4, ensure_ascii=False)
        logger.log_state(state, old_room)
    telegrammer.disconnect()
    logger.close()


def load_inventory():
    items = {}
    telegrammer.send_msg("🎒 Посмотреть инвентарь")
    while True:
        message = telegrammer.get_message()
        inventory = message.text
        replies = message.replies
        for i in Constants.inventory_re.finditer(inventory):
            items[i.group(1)] = int(i.group(2))
        if '▶ Дальше' in replies:
            telegrammer.send_msg('▶ Дальше')
        else:
            telegrammer.send_msg('↪ В коридор')
            return items


def sell(state: BotState):
    items = SellItems.get_items(state)
    telegrammer.send_msg("🎒 Посмотреть инвентарь")
    for key, value in items.items():
        for i in range(value):
            telegrammer.send_msg('💰 Продать {}'.format(key))
            state.current_items[key] -= 1
    telegrammer.send_msg('↪ В коридор')


def check_rooms(path_to_repo):
    def print_rooms(rooms, group_name, formatter):
        print(group_name)
        for i in rooms:
            print('\t{}'.format(formatter(i)))

    changed, removed, added = Room.check_rooms(path_to_repo, Rooms.rooms)
    print_rooms(changed, "Изменённые:", lambda r: '{} ({})'.format(r.name, '; '.join(list(r.hashes.keys()))))
    print_rooms(removed, "Удаленные:", lambda p: p)
    print_rooms(added, "Новые:", lambda p: p)


def battle(weapon):
    telegrammer.send_msg(weapon)
    while True:
        msg = telegrammer.get_message()
        for r in msg.replies:
            if weapon in r:
                telegrammer.send_msg(r)
        else:
            break


def main():
    parser = argparse.ArgumentParser(description='Почти автоматически играет в @rog_bot.')
    parser.add_argument('-i', '--inventory', dest='inventory', action='store_true',
                        help='Обновляет инвентарь из игры. Бот должен находится в коридоре')
    parser.add_argument('-s', '--sell', dest='sell', action='store_true',
                        help='Продает лишние вещи. Бот должен находится в коридоре')
    parser.add_argument('-g', '--game', dest='game', action='store_true',
                        help='Запускает бота. Для запуска может потребоваться вручную отправить сообщение')
    parser.add_argument('-b', '--battle', dest='weapon', type=str,
                        help='Запускает битву указанным оружием.')
    parser.add_argument('--check', dest='path_to_repo', type=str,
                        help='Проверяет, не изменились ли комнаты')
    args = parser.parse_args()

    bot_state = {}
    if os.path.isfile('bot_state.json'):
        with open('bot_state.json', 'r', encoding='utf-8') as f:
            bot_state = json.load(f)
    state = BotState.BotState(bot_state)

    if args.path_to_repo:
        check_rooms(args.path_to_repo)

    if args.inventory or args.sell or args.game or args.weapon:
        telegrammer.start()
    if args.weapon:
        battle(args.weapon)
    if args.inventory:
        state.current_items = load_inventory()
    if args.sell:
        sell(state)
    if args.game:
        bot(state)
