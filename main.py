# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

methods = ['zb1', 'mr1',
           'titer',
           'refs', 'titls', 'texts',
           'ref1',
           'uT1', 'uM1',
           'tiref', 'teref', 'tite']
sources = {
    'zb1': pd.read_pickle('data/zbByMsc.pkl'),
    'mr1': pd.read_pickle('data/mrByMsc.pkl')
}
layout = go.Layout(barmode='group',
                   xaxis={'type': 'category', 'title': 'msc', 'mirror': True},
                   yaxis={'title': 'f1-score', 'range': [0, 1], 'mirror': True},
                   template='simple_white')

with open('Readme.md', 'r') as f:
    readme_file = f.read()


def get_data(source, minimum, sort):
    z = get_data_frame(source, minimum, sort)
    data = []
    for method in methods:
        data.append(go.Bar(x=z.msc, y=z[f'f{method}'], name=method))
    return data


def get_data_frame(source, minimum, sort):
    z = sources[source]
    z = pd.DataFrame(z[z['p'] >= minimum])
    z = z.sort_values(by=[f'f{sort}'], ascending=False)
    return z


tc: pd.DataFrame = pd.read_pickle('data/titerConfZb.pkl')


def get_count(i: int, j: int) -> int:
    c = tc[(tc['t'] == i) & (tc['p'] == j)]['count']
    if c.size == 1:
        return c.values[0]
    else:
        return 0


def get_conf_matrix(minimum):
    label = get_conf_label(minimum)
    z = np.ndarray(shape=(label.size, label.size), dtype=int)
    i = 0
    for x in label:
        j = 0
        for y in label:
            z[i, j] = get_count(x, y)
            j += 1
        i += 1
    return z


def get_conf_label(minimum):
    titer_conf_label = get_data_frame('zb1', minimum, 'mr1')['msc'].values
    return titer_conf_label


def get_conf_label_as_string(minimum):
    label = get_data_frame('zb1', minimum, 'mr1')['msc'].values.astype(str)
    label2 = []
    for label in label:
        label2.append(label + "*")
    return label2


def get_heatmap(minimum):
    return {
        'data': [go.Heatmap(
            z=get_conf_matrix(minimum),
            x=get_conf_label_as_string(minimum), y=get_conf_label_as_string(minimum),
            colorscale='Blues')],
        'layout': {
            'yaxis': {
                'scaleanchor': 'x'
            },
        }}


app.layout = html.Div(children=[
    dcc.Markdown(readme_file),
    html.Div([
        html.Label('Sort by', htmlFor='ref'),
        dcc.Dropdown(
            id='sort',
            options=[{'label': i, 'value': i} for i in methods],
            value='mr1'
        ),
        html.Label('Reference dataset', htmlFor='ref')
        ,
        dcc.RadioItems(
            id='ref',
            options=[{'label': 'zbMATH (zb1)', 'value': 'zb1'},
                     {'label': 'Mathematical Reviews (mr1)', 'value': 'mr1'}],
            value='zb1',
            labelStyle={'display': 'inline-block'}
        ),
        html.Label('Minimum test values', htmlFor='minimum')
        ,
        dcc.Input(
            id='minimum',
            value=200,
            type='number'
        ),
    ],
        style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(
        id='example-graph'
    ),
    dcc.Graph(
        id='heatmap'
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in sources['zb1'].columns],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_current=0,
        page_size=10,
    )
])


@app.callback(
    [Output('example-graph', 'figure'), Output('table', 'data'), Output('heatmap', 'figure')],
    [Input('ref', 'value'), Input('minimum', 'value'), Input('sort', 'value')])
def update_output_div(ref, minimum, sort):
    return {
               'data': get_data(ref, minimum, sort),
               'layout': layout
           }, get_data_frame(ref, minimum, sort).to_dict('records'), get_heatmap(minimum)


server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
