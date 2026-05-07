# Git hooks

Чтобы перед каждым коммитом автоматически обновлялись контрольные суммы итогового PDF в README, подключите локальные hooks:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task hooks
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
git config core.hooksPath .githooks
```

{{#endtab}}

{{#endtabs}}

Для работы hook нужен Python-пакет `python-dotenv`. Он указан в `requirements.txt`.

Если окружение еще не подготовлено, установите зависимости:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task deps
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
pip install -r requirements.txt
```

{{#endtab}}

{{#endtabs}}

Hook считает хэши текущего PDF алгоритмами из стандартного `hashlib`. Если PDF отсутствует, README не меняется и коммит продолжается со старым значением.
