import plotly.graph_objects as go

categories = [
    "Скорость старта разработки",
    "Качество кода",
    "Устойчивость к изменениям",
    "Простота внедрения",
    "Удобство сопровождения",
    "Тестовое покрытие"
]

data = {
    "TDD": [5, 9, 9, 4, 9, 10],
    "Test-after development": [7, 7, 7, 7, 7, 7],
    "Waterfall": [4, 6, 3, 5, 5, 4],
    "Iterative / Agile": [8, 8, 8, 7, 8, 7],
    "Code-and-Fix": [9, 3, 2, 9, 2, 1],
}

fig = go.Figure()

for method, values in data.items():
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=method
    ))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 10],
            dtick=2
        ),
        angularaxis=dict(
            showline=False  # ← убирает эту линию
        )        
    ),  
    width=950,
    height=750,
    showlegend=True
)

# fig.show()

fig.update_layout(font_size=14, margin=dict(b=0, t=0, l=180, r=0))
fig.write_image("figures/methodologies.pdf")