## Установка
```bash
git clone https://github.com/Salvatore112/console-chat.git
cd console-chat.git
```

```bash
mkdir -p ~/chat-app-1.0 && \
cp -r src SPECS ~/chat-app-1.0/ && \
cd ~ && \
tar -czvf chat-app-1.0.tar.gz chat-app-1.0/ && \
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} && \
mv chat-app-1.0.tar.gz ~/rpmbuild/SOURCES/ && \
mv ~/chat-app-1.0/SPECS/* ~/rpmbuild/SPECS/
```
