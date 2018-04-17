import json
import os
import socket
from sys import argv, stdin
from threading import Thread
from time import sleep

sock = socket.socket()
if len(argv) == 3:
    sock.connect((argv[1], int(argv[2])))
else:
    from Bot import Config
    if not Config.test:
        print('[WARNING] Test mode not enabled in Bot.Config!')
    sock.connect((Config.test_host, Config.test_port))



def listener():
    global sock
    while sock:
        size_data = sock.recv(4)
        assert size_data
        size = int.from_bytes(size_data, byteorder='little')
        data: bytes = sock.recv(size)
        command = json.loads(data.decode('utf-8'))

        if command['action'] == 'send':
            print('[SEND] {}\n{}'.format(command['entity'], command['content']))
        elif command['action'] == 'receive':
            print('[RECEIVE] {} from {}\n{}\n{}'.format(
                command['date'],
                'bot' if command['from_bot'] else 'user',
                command['text'],
                command['replies']
            ))
        elif command['action'] == 'connect':
            print('[CONNECT]')
        elif command['action'] == 'disconnect':
            print('[DISCONNECT]')
            sock.close()


def reader():
    global sock
    while sock:
        print('\tenter message>')
        ln = stdin.readline().strip('\n')
        if ln.startswith('/load'):
            fName = os.path.join('tester', ln.split(' ', 1)[1] + '.json')
            with open(fName, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif ln == '/timeout':
            data = {'action': 'timeout'}
        else:
            message = (ln + '\n' + stdin.read()).rstrip('\n')
            print('\tenter replies>')
            replies = stdin.read().rstrip('\n').split('\n')
            data = {'action': 'message', 'text': message, 'replies': replies}
        command = json.dumps(data, ensure_ascii=False).encode('utf-8')
        sock.send(len(command).to_bytes(4, byteorder='little') + command)
        print('\tsent!')


Thread(target=listener).start()
Thread(target=reader).start()
try:
    while sock:
        sleep(0.1)
except KeyboardInterrupt:
    sock.close()
    sock = None
