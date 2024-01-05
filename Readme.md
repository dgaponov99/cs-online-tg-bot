## cs-online-tg-bot cs1.6 bot

ТГ бот для сервера кс 1.6, позволяющий отобразить список онлайн-игроков на сервере

### Возможности:
- `сервер` отобразится список игроков на сервере

### Переменные окружения:
- `CS_SERVER_IP` IP игрового сервер (ex. 123.123.123.123)
- `CS_SERVER_PORT` Порт игрового сервера (ex. 27015)
- `TG_TOKEN` Токен бота ТГ

### docker-compose:
```yaml
version: "3.9"
services:
  my-cs-bot:
    image: dgaponov99/cs-online-tg-bot
    container_name: my-cs-bot
    restart: always
    environment:
      - CS_SERVER_IP=IP игрового сервер (ex. 123.123.123.123)
      - CS_SERVER_PORT=Порт игрового сервера (ex. 27015)
      - TG_TOKEN=Токен бота ТГ
```