## Библиотеки

В ходе разработки приложения были использованы следующие Python-библиотеки:

- socket -- для сетевого взаимодействия

- threading -- для многопоточности

- argparse -- для обработки аргументов командной строки

- logging -- для логирования работы приложения

Все они входят в стандартную библиотеку Python

## Установка

```bash
git clone https://github.com/Salvatore112/console-chat.git
cd console-chat.git
```

```bash
mkdir -p ~/chat-app-1.0/src
cp -r src/* ~/chat-app-1.0/src/
cp chat-app.spec ~/chat-app-1.0/
cd ~
tar -czvf chat-app-1.0.tar.gz chat-app-1.0/
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mv chat-app-1.0.tar.gz ~/rpmbuild/SOURCES/
cp ~/chat-app-1.0/chat-app.spec ~/rpmbuild/SPECS/
```

### DEBIAN + DEBIAN Based distros

```bash
sudo docker run -it --rm -v ~/rpmbuild:/rpmbuild oraclelinux:8.10 /bin/bash -c "
    dnf install -y rpm-build python3 &&
    cd /rpmbuild/SPECS &&
    rpmbuild -ba --define '_topdir /rpmbuild' chat-app.spec
"
```
```bash
sudo apt-get install alien
cd ~/rpmbuild/RPMS/noarch/
sudo alien --to-deb chat-app-1.0-1.el8.noarch.rpm
sudo dpkg -i chat-app_1.0-2_all.deb
```

### Red Hat + Red Hat Based distros

```bash
sudo dnf install -y rpm-build python3
cd ~/rpmbuild/SPECS
rpmbuild -ba --define '_topdir /home/yourusername/rpmbuild' chat-app.spec
```
```bash
sudo dnf install -y ~/rpmbuild/RPMS/noarch/chat-app-1.0-1.el8.noarch.rpm
```

## Использование 

### Запуск сервера
```bash
chat-server [--port PORT] [--host IP]
```

### Запуск клиента
```bash
chat-client [--port PORT] [--host IP]
```

`--port` - указать порт (по умолчанию: 5555)

`--host` - указать IP для прослушивания (по умолчанию: localhost)`