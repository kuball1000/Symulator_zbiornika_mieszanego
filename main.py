import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

Tf = 300-273
Tq = 400-273
epsilon = 1

def PID(Kp, setpoint, measurement, deltat):
    global time, integral, time_prev, e_prev
    offset = 320 -273
    e = setpoint - measurement
    P = Kp * e
    Ti = 1.2*deltat
    Td = 0.05*deltat
    integral = integral + Ti/deltat * e * (time - time_prev)
    D = Td/deltat * (e - e_prev) / (time - time_prev)
    MV = offset + P + integral + D
    e_prev = e
    time_prev = time
    return MV

def system(temp, Tq, epsilon, tau, Q, Tf):
    dTdt = 1 / (tau * (1 + epsilon)) * (Tf - temp) + Q / (1 + epsilon) * (Tq - temp)
    return dTdt

def simulate_system(setpoint, Kp, Tf, tau, C, kq, Aq, s, y0, deltat):
    global time, integral, time_prev, e_prev
    Q = (kq*Aq)/C
    time_prev = 0
    e_prev = setpoint - y0 + 2
    y_sol = [y0]
    t_sol = [time_prev]
    Tq = 320-273
    q_sol = [Tq]
    integral = 0
    Oddane = [(Tq-y0)*kq*Aq]
    Całkowite_oddane = [(Tq-y0)*kq*Aq]
    for i in range(1, int(s*(1/deltat))):
        time = i * deltat
        Tq = PID(Kp, setpoint, y_sol[-1], deltat)
        yi = y_sol[-1] + system(y_sol[-1], Tq, epsilon, tau, Q, Tf)*deltat
        t_sol.append(time)
        y_sol.append(yi)
        q_sol.append(Tq)
        cieplo_oddane_przez_plaszcz = (q_sol[-1]-y_sol[-1])*kq*Aq
        Całkowite_oddane.append(Całkowite_oddane[-1]+cieplo_oddane_przez_plaszcz)
        Oddane.append(cieplo_oddane_przez_plaszcz)
        time_prev = time
    return t_sol, y_sol, q_sol, Oddane, Całkowite_oddane

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

heading = html.H4(
    "Symulator zbiornika mieszanego, z płaszczem termicznym,  ogrzewanego za pomocą cieczy", className="bg-primary text-white p-4"
)
K_p = html.Div(
    [dbc.Label("Kp współczynnik wzmocnienia", html_for="K_p"), dbc.Input(id="K_p", type="number", value=0.2, min=0, max=9, step=0.1, style={'width': '100px'})],
    className="mt-2",
)
T_f = html.Div(
    [dbc.Label("Tf Temperatura na wlocie [°C]", html_for="T_f"), dbc.Input(id="T_f", type="number", value=27, min=0, max=99, style={'width': '100px'})],
    className="mt-2",
)
tau = html.Div(
    [dbc.Label("Czas pobytu substancji 𝜏 [s]", html_for="tau"), dbc.Input(id="tau", type="number", value=4, min=0, max=99, step=0.2, style={'width': '100px'})],
    className="mt-2",
)
C = html.Div(
    [dbc.Label("Pojemność cieplna sybstancji ogrzewanej  [J/°C]", html_for="C"), dbc.Input(id="C", type="number", value=100, min=50, max=150, step=1, style={'width': '100px'})],
    className="mt-2",
)
kq = html.Div(
    [dbc.Label("Współczynnik wymiany ciepła między płaszczem wodnym a zbiornikiem [W/(m\u00b2 · K)]", html_for="kq"), dbc.Input(id="kq", type="number", value=3.4, min=0, max=10, step=0.1, style={'width': '100px'})],
    className="mt-2",
)
Aq = html.Div(
    [dbc.Label("Powierzchnia przekazywania ciepła w płaszczu wodnym [m\u00b2]", html_for="Aq"), dbc.Input(id="Aq", type="number", value=42, min=10, max=100, step=1, style={'width': '100px'})],
    className="mt-2",
)
K = html.Div(
    [dbc.Label("Temperatura zadana [°C]", html_for="K"), dbc.Input(id="K", type="number", value=37, min=0, max=99   , style={'width': '100px'})],
    className="mt-2",
)
s = html.Div(
    [dbc.Label("Czas symulacji [s]", html_for="s"), dbc.Input(id="s", type="number", value=20, min=0, max=100, style={'width': '100px'})],
    className="mt-2",
)
y0 = html.Div(
    [dbc.Label("Początkowa temperatura w zbiorniku [°C]", html_for="y0"), dbc.Input(id="y0", type="number", value=27, min=0, max=200, style={'width': '100px'})],
    className="mt-2",
)
deltat = html.Div(
    [dbc.Label("Tp [s]", html_for="deltat"), dbc.Input(id="deltat", type="number", value=0.1, min=0.1, max=1, step=0.1, style={'width': '100px'})],
    className="mt-2",
)

control_panel = dbc.Card(
    dbc.CardBody(
        [K_p, T_f, tau, C, kq, Aq, K, s, y0, deltat],
        className="bg-light",
        style={'width': '390px'}
    )
)

graph_and_image_div = dbc.Col([
    html.Div([html.Div(id="error_msg", className="text-danger"), dcc.Graph(id="graph"),dcc.Graph(id="graph2")]),
], md=9)

app.layout = dbc.Container(
    [heading, dbc.Row([dbc.Col(control_panel, md=5, style={'max-width': '416px'}), graph_and_image_div])],
    fluid=True
)

@app.callback(
    Output("graph", "figure"),
    Output("graph2", "figure"),
    Output("error_msg", "children"),
    Input("K_p", "value"),
    Input("T_f", "value"),
    Input("tau", "value"),
    Input("C", "value"),
    Input("kq", "value"),
    Input("Aq", "value"),
    Input("K", "value"),
    Input("s", "value"),
    Input("y0", "value"),
    Input("deltat", "value"),
)

def callback(K_p, T_f , tau, C, kq, Aq, K, s, y0, deltat):
    if any(v is None for v in [K_p, T_f, tau, C, kq, Aq, K, s, y0, deltat]):
        return {}, "Please enter all values"

    t_sol, y_sol, q_sol, oddane, przekazane_cieplo = simulate_system(K, K_p,  T_f, tau, C, kq, Aq, int(s), y0, deltat)
    to_plot = pd.DataFrame(list(zip(t_sol, y_sol, q_sol)), columns=["Czas [s]", "Temperatura w zbiorniku [°C]",
                                                                   "Temperatura substancji ogrzewającej [°C]"])
    fig = px.line(to_plot, x="Czas [s]", y=["Temperatura w zbiorniku [°C]", "Temperatura substancji ogrzewającej [°C]"]). \
        update_layout(xaxis_title="Czas [s]", yaxis_title="Temperatura [°C]")
    fig.update_layout(title_text='Symulacja regulacji PID')
    fig.update_layout(legend={'title_text': ''})
    fig.update_traces(hovertemplate='Czas: %{x:.1f} [s]<br>Temperatura: %{y:.1f} [°C]')

    to_plot2 = pd.DataFrame(list(zip(t_sol,oddane,przekazane_cieplo)), columns=["Czas [s]", "Ciepło oddane w czasie Tp [J]","Całkowite oddane ciepło [J]"])
    fig2 = px.line(to_plot2, x="Czas [s]", y=["Ciepło oddane w czasie Tp [J]", "Całkowite oddane ciepło [J]"])
    fig2.update_layout(xaxis_title="Czas [s]", yaxis_title="Ciepło oddane [J]")
    fig2.update_layout(title_text='Ilość przekazywanego ciepła')
    fig2.update_layout(legend={'title_text': ''})
    fig2.update_traces(hovertemplate='Czas: %{x:.1f} [s]<br>Ciepło oddane: %{y:.1f} [J]')

    return fig, fig2, None

if __name__ == "__main__":
    app.run_server(debug=True)