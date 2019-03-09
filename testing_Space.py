import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar_children = [
    dbc.NavItem(dbc.NavLink("Page 1", href="/page-1")),
    dbc.NavItem(dbc.NavLink("Page 2", href="/page-2")),
]

navbar = dbc.Navbar(navbar_children, sticky="top")

# define content for page 1
page1 = dbc.Card(
    [
        dbc.CardTitle("Page 1 contents"),
        dbc.CardText("You can replace this with whatever you like"),
    ],
    body=True,
)

# define content for page 2

tab1 = dbc.Card(
    [
        dbc.CardTitle("Page 2, tab 1 contents"),
        dbc.CardText("You can replace this with whatever you like"),
    ],
    body=True,
)

tab2 = dbc.Card(
    [
        dbc.CardTitle("Page 2, tab 1 contents"),
        dbc.CardText("Let's write something different here for fun"),
    ],
    body=True,
)

page2 = dbc.Tabs(
    [
        dbc.Tab(tab1, label="Tab 1", className="mt-3"),
        dbc.Tab(tab2, label="Tab 2", className="mt-3"),
    ]
)

# define page layout
app.layout = html.Div(
    [
        dcc.Location(id="url", pathname="/page-1"),
        navbar,
        dbc.Container(id="content", style={"padding": "20px"}),
    ]
)


# create callback for modifying page layout
@app.callback(Output("content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page-1":
        return page1
    if pathname == "/page-2":
        return page2
    # if not recognised, return 404 message
    return html.P("404 - page not found")


if __name__ == "__main__":
    app.run_server(debug="True")
