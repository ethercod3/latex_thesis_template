import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def add_box(ax, x, y, w, h, title, subtitle="", fontsize=12):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5,
        edgecolor="black",
        facecolor="#EAE6F8"
    )
    ax.add_patch(box)

    text = title if not subtitle else f"{title}\n{subtitle}"
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize
    )

def add_arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            lw=1.4,
            shrinkA=8,
            shrinkB=8
        )
    )

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Заголовок
ax.text(
    0.5, 0.96,
    "Компонентная структура приложения Vault",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)

# Верхний слой — точки входа
add_box(ax, 0.12, 0.78, 0.18, 0.10, "main.py", "Точка входа")
add_box(ax, 0.41, 0.78, 0.18, 0.10, "cli.py", "CLI-интерфейс")
add_box(ax, 0.70, 0.78, 0.18, 0.10, "api.py", "HTTP API")

# Средний слой — прикладная логика
add_box(ax, 0.10, 0.52, 0.18, 0.11, "auth", "Аутентификация")
add_box(ax, 0.31, 0.52, 0.18, 0.11, "crypto", "Шифрование /\nрасшифрование")
add_box(ax, 0.52, 0.52, 0.18, 0.11, "key_manager", "Управление ключами")
add_box(ax, 0.73, 0.52, 0.18, 0.11, "schemas, db_schemas", "Валидация и контракты")

# Нижний слой — инфраструктура
add_box(ax, 0.24, 0.24, 0.20, 0.11, "db.py", "Слой доступа к данным")
add_box(ax, 0.56, 0.24, 0.20, 0.11, "settings.py", "Конфигурация")

# Связи от точек входа
for x in [0.21, 0.50, 0.79]:
    add_arrow(ax, x, 0.78, 0.19, 0.63)  # auth
    add_arrow(ax, x, 0.78, 0.40, 0.63)  # crypto
    add_arrow(ax, x, 0.78, 0.61, 0.63)  # key_manager
    add_arrow(ax, x, 0.78, 0.82, 0.63)  # validation

# Внутренние связи логики
add_arrow(ax, 0.40, 0.52, 0.61, 0.63)  # crypto -> key_manager
add_arrow(ax, 0.61, 0.52, 0.34, 0.35)  # key_manager -> db
add_arrow(ax, 0.40, 0.52, 0.34, 0.35)  # crypto -> db
add_arrow(ax, 0.19, 0.52, 0.34, 0.35)  # auth -> db

# Конфигурация
add_arrow(ax, 0.19, 0.52, 0.66, 0.35)  # auth -> settings
add_arrow(ax, 0.40, 0.52, 0.66, 0.35)  # crypto -> settings
add_arrow(ax, 0.61, 0.52, 0.66, 0.35)  # key_manager -> settings
add_arrow(ax, 0.82, 0.52, 0.66, 0.35)  # validation -> settings
add_arrow(ax, 0.34, 0.24, 0.66, 0.35)  # db -> settings

# Подписи слоев
ax.text(0.03, 0.83, "Слой\nвхода", fontsize=11, va="center")
ax.text(0.03, 0.57, "Прикладной\nслой", fontsize=11, va="center")
ax.text(0.03, 0.29, "Инфраструктурный\nслой", fontsize=11, va="center")

plt.tight_layout()
plt.show()