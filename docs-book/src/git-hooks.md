# Git hooks

Чтобы перед каждым коммитом автоматически обновлялись контрольные суммы итогового PDF в README, подключите локальные hooks:

```bash
git config core.hooksPath .githooks
```

Для работы hook нужен Python-пакет `python-dotenv`. Он указан в `requirements.txt`.

Если окружение еще не подготовлено, установите зависимости:

```bash
pip install -r requirements.txt
```

Hook считает хэши текущего PDF алгоритмами из стандартного `hashlib`. Если PDF отсутствует, README не меняется и коммит продолжается со старым значением.
