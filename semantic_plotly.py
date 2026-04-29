import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import plotly.graph_objects as go


import plotly.figure_factory as ff

data_matrix = [['Семантическое значение', 'Модуль'],
            ["Точка входа", "main.py, vault/cli.py, vault/api.py"],
            ["Слой доступа к данным", "vault/db.py (репозиторий и ORM-модели)"],
            ["Слой валидации контрактов", "vault/schemas.py, vault/db_schemas.py"],
            ["Конфигурационный слой", "vault/settings.py и переменные окружения"]
            ]

fig = ff.create_table(data_matrix)

fig.update_layout(font_size=14, margin=dict(b=15))
fig.write_image("semantic.pdf")

# fig.show()    