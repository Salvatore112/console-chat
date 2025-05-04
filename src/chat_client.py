#!/usr/bin/env python3.14
"""
TCP-клиент для консольного чата.

Клиент подключается к серверу, отправляет и получает сообщения,
обрабатывает подтверждения о доставке.
"""

import argparse
import socket
import select
import sys
from typing import Tuple


class ChatClient:
    def __init__(self, server_host: str = "localhost", server_port: int = 5555):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.username = None
        self.running = False

    def start(self) -> None:
        try:
            self._get_username()
            self._connect_to_server()
            self._main_loop()
        except KeyboardInterrupt:
            print("\nКлиент остановлен")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.stop()

    def _get_username(self) -> None:
        while True:
            self.username = input("Введите имя пользователя: ").strip()
            if self.username:
                break
            print("Имя пользователя не может быть пустым")

    def _connect_to_server(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

        self.socket.send(self.username.encode("utf-8"))

        response = self.socket.recv(1024).decode("utf-8")

        if response.startswith("ERROR"):
            raise ConnectionError(response)

        print(f"Подключено к серверу. {response}")
        self.running = True

    def _main_loop(self) -> None:
        while self.running:
            try:
                sockets_list = [sys.stdin, self.socket]
                read_sockets, _, _ = select.select(sockets_list, [], [])

                for notified_socket in read_sockets:
                    if notified_socket == self.socket:
                        message = self.socket.recv(1024).decode("utf-8")
                        if not message:
                            raise ConnectionError("Сервер отключился")

                        self._handle_server_message(message)
                    else:
                        message = sys.stdin.readline().strip()
                        if message.lower() == "/exit":
                            self.running = False
                            break
                        if message:
                            self._send_message(message)

            except ConnectionError as e:
                print(f"Ошибка подключения: {e}")
                self.running = False
            except Exception as e:
                print(f"Ошибка: {e}")
                self.running = False

    def _handle_server_message(self, message: str) -> None:
        if message.startswith("OK:"):
            print(f"\n[Подтверждение] {message[3:].strip()}")
        elif message.startswith("ERROR:"):
            print(f"\n[Ошибка] {message[6:].strip()}")
        else:
            print(f"\n[Сообщение] {message}")

        print(f"[{self.username}] > ", end="", flush=True)

    def _send_message(self, message: str) -> None:
        try:
            self.socket.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            self.running = False

    def stop(self) -> None:
        if self.socket:
            self.socket.close()
        print("Клиент завершил работу")


def parse_args():
    parser = argparse.ArgumentParser(description="Запуск клиента чата")
    parser.add_argument("--host", default="localhost", help="Хост сервера")
    parser.add_argument("--port", type=int, default=5555, help="Порт сервера")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    client = ChatClient(args.host, args.port)
    client.start()
