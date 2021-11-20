import dash
from dash import dcc
from dash import html
import numpy as np
import datetime
from dash.dependencies import Output, Input
from funciones import getCotizaciones

# lista pares de monedas mas importante, BITCOIN, ETHERUM, MATIC
listado_valores = ['XXBTZEUR', 'XXBTZUSD', 'XETHZEUR', 'XETHZUSD',
                   'MATICEUR', 'MATICUSD', 'XXLMZEUR', 'XXLMZUSD']

# sacamos fecha de hoy y restamos horas para ir acumulando datos
hasta = datetime.datetime.now()
desde = hasta - datetime.timedelta(hours=4)

# llamamos a la funcion de obtener cotizaciones con los pares y rango de fechas
data = getCotizaciones(listado_valores, desde, hasta)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Analisis Criptomonedas"
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="⚡", className="header-emoji"),
                html.H1(
                    children="Analisis Criptomonedas", className="header-title"
                ),
                html.P(
                    children="Analisis de las Criptomonedas mas relevantes",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Criptomoneda",
                                 className="menu-title"),
                        dcc.Dropdown(
                            id="filtro-cripto",
                            options=[
                                {"label": cripto, "value": cripto}
                                for cripto in np.sort(data.cripto.unique())
                            ],
                            value="XXBTZ",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Divisa", className="menu-title"),
                        dcc.Dropdown(
                            id="filtro-valor",
                            options=[
                                {"label": valor, "value": valor}
                                for valor in data.valor.unique()
                            ],
                            value="USD",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="grafica-precio", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="grafica-vwap", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ])


@app.callback(
    [Output("grafica-precio", "figure"), Output("grafica-vwap", "figure")],
    [
        Input("filtro-cripto", "value"),
        Input("filtro-valor", "value"),
    ],
)
def update_charts(cripto, valor):
    mask = (
            (data.cripto == cripto) & (data.valor == valor)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Price"],
                "type": "lines",
                "name": "Precio",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
                "color": ["#17B897"],
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["vwap"],
                "type": "lines",
                "name": "VWAP",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
                "color": ["#E12D39"],
            },
        ],
        "layout": {
            "title": {
                "text": "Price",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},

        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Volume"],
                "type": "bar",
            },
        ],
        "layout": {
            "title": {
                "text": "Volume",
                "x": 0.05,
                "xanchor": "left"
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
