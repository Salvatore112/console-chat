#!/usr/bin/env python3.14
"""
TCP-сервер для консольного чата.

Сервер принимает подключения от клиентов, маршрутизирует сообщения между ними,
отправляет подтверждения о доставке и ведет логирование событий.
"""

import argparse
import logging
import select
import socket
import sys
from typing import Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("chat_server.log"), logging.StreamHandler()],
)
logger = logging.getLogger("ChatServer")


class ChatServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[socket.socket, Tuple[str, str]] = {}
        self.message_buffer: Dict[str, str] = {}

    def start(self) -> None:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logger.info(f"Сервер запущен на {self.host}:{self.port}")

            self._main_loop()

        except Exception as e:
            logger.error(f"Ошибка сервера: {e}")
        finally:
            self.shutdown()

    def _main_loop(self) -> None:
        while True:
            try:
                read_sockets, _, exception_sockets = select.select(
                    [self.server_socket] + list(self.clients.keys()),
                    [],
                    list(self.clients.keys()),
                )

                for notified_socket in read_sockets:
                    if notified_socket == self.server_socket:
                        self._accept_new_connection()
                    else:
                        self._handle_client_message(notified_socket)

                for notified_socket in exception_sockets:
                    self._remove_client(notified_socket)

            except KeyboardInterrupt:
                logger.info("Сервер остановлен администратором")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")

    def _accept_new_connection(self) -> None:
        client_socket, client_address = self.server_socket.accept()

        try:
            username = client_socket.recv(1024).decode("utf-8").strip()

            if not username:
                raise ValueError("Пустое имя пользователя")

            if any(username == u for u, _ in self.clients.values()):
                client_socket.send("ERROR: Имя пользователя уже занято".encode("utf-8"))
                client_socket.close()
                return

            self.clients[client_socket] = (username, client_address)
            logger.info(f"Новое подключение: {username} из {client_address}")
            client_socket.send("OK: Вы подключены к чату".encode("utf-8"))

            if username in self.message_buffer:
                client_socket.send(self.message_buffer[username].encode("utf-8"))
                del self.message_buffer[username]

        except Exception as e:
            logger.error(f"Ошибка при подключении клиента: {e}")
            client_socket.close()

    def _handle_client_message(self, client_socket: socket.socket) -> None:
        try:
            message = client_socket.recv(1024).decode("utf-8").strip()

            if not message:
                raise ConnectionError("Пустое сообщение (возможно, отключение)")

            username, address = self.clients[client_socket]
            logger.info(f"Сообщение от {username}: {message}")

            if message.startswith("@") and ":" in message:
                recipient, msg = message[1:].split(":", 1)
                recipient = recipient.strip()
                msg = msg.strip()

                if not msg:
                    client_socket.send("ERROR: Пустое сообщение".encode("utf-8"))
                    return

                self._send_private_message(username, recipient, msg)
            else:
                self._broadcast_message(username, message)

        except ConnectionError as e:
            logger.info(f"Клиент отключился: {self.clients[client_socket][0]}")
            self._remove_client(client_socket)
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            client_socket.send(f"ERROR: {e}".encode("utf-8"))

    def _send_private_message(self, sender: str, recipient: str, message: str) -> None:
        formatted_message = f"PM от {sender}: {message}"
        recipient_socket = None

        for sock, (username, _) in self.clients.items():
            if username == recipient:
                recipient_socket = sock
                break

        if recipient_socket:
            try:
                recipient_socket.send(formatted_message.encode("utf-8"))
                for sock, (username, _) in self.clients.items():
                    if username == sender:
                        sock.send(
                            f"OK: Сообщение доставлено {recipient}".encode("utf-8")
                        )
                        break
                logger.info(f"Сообщение от {sender} доставлено {recipient}")
            except Exception as e:
                logger.error(f"Ошибка доставки сообщения {sender} -> {recipient}: {e}")
        else:
            self.message_buffer[recipient] = formatted_message
            for sock, (username, _) in self.clients.items():
                if username == sender:
                    sock.send(
                        f"OK: Сообщение будет доставлено когда {recipient} подключится".encode(
                            "utf-8"
                        )
                    )
                    break
            logger.info(f"Сообщение от {sender} для {recipient} буферизировано")

    def _broadcast_message(self, sender: str, message: str) -> None:
        formatted_message = f"{sender}: {message}"
        for sock, (username, _) in self.clients.items():
            if username != sender:
                try:
                    sock.send(formatted_message.encode("utf-8"))
                except Exception as e:
                    logger.error(
                        f"Ошибка рассылки сообщения от {sender} к {username}: {e}"
                    )

        for sock, (username, _) in self.clients.items():
            if username == sender:
                sock.send("OK: Сообщение доставлено всем".encode("utf-8"))
                break
        logger.info(f"Сообщение от {sender} доставлено всем")

    def _remove_client(self, client_socket: socket.socket) -> None:
        if client_socket in self.clients:
            username, address = self.clients[client_socket]
            logger.info(f"Клиент отключен: {username} из {address}")
            del self.clients[client_socket]
            client_socket.close()

    def shutdown(self) -> None:
        logger.info("Завершение работы сервера...")
        for client_socket in list(self.clients.keys()):
            self._remove_client(client_socket)

        if self.server_socket:
            self.server_socket.close()
        logger.info("Сервер остановлен")


def parse_args():
    parser = argparse.ArgumentParser(description="Запуск сервера чата")
    parser.add_argument("--host", default="0.0.0.0", help="Хост для прослушивания")
    parser.add_argument("--port", type=int, default=5555, help="Порт для прослушивания")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = ChatServer(args.host, args.port)
    server.start()
