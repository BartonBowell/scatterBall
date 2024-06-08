import pandas as pd
import panel as pn
import plotly.graph_objs as go
from pybaseball import batting_stats, pitching_stats

pn.extension('plotly')
team_map = {
    "BostonRedSox": "BOS", "ChicagoCubs": "CHC", "CincinnatiReds": "CIN", "HoustonAstros": "HOU",
    "KansasCityRoyals": "KCR", "LosAngelesDodgers": "LAD", "MiamiMarlins": "MIA", "NewYorkYankees": "NYY",
    "OaklandAthletics": "OAK", "SanDiegoPadres": "SDP", "SeattleMariners": "SEA", "StLouisCardinals": "STL",
    "TampaBayRays": "TBR", "TexasRangers": "TEX", "WashingtonNationals": "WSN", "ChicagoWhiteSox": "CHW",
    "MilwaukeeBrewers": "MIL", "ArizonaDBacks": "ARI", "AtlantaBraves": "ATL", "ColoradoRockies": "COL",
    "DetroitTigers": "DET", "LosAngelesAngels": "LAA", "BaltimoreOrioles": "BAL", "ClevelandGuardians": "CLE",
    "MinnesotaTwins": "MIN", "NewYorkMets": "NYM", "PhiladelphiaPhillies": "PHI", "PittsburghPirates": "PIT",
    "SanFranciscoGiants": "SFG", "TorontoBlueJays": "TOR"
}

# Define colors for each team abbreviation
team_colors = {
    'ARI': ['#A71930', '#E3D4AD'], 'ATL': ['#CE1141', '#13274F'], 'BAL': ['#DF4601', '#000000'],
    'BOS': ['#BD3039', '#0C2340'], 'CHC': ['#0E3386', '#CC3433'], 'CHW': ['#27251F', '#C4CED4'],
    'CIN': ['#C6011F', '#000000'], 'CLE': ['#00385D', '#E50022'], 'COL': ['#333366', '#C4CED4'],
    'DET': ['#0C2340', '#FA4616'], 'HOU': ['#002D62', '#EB6E1F'], 'KCR': ['#004687', '#BD9B60'],
    'LAA': ['#003263', '#BA0021'], 'LAD': ['#005A9C', '#A5ACAF'], 'MIA': ['#00A3E0', '#EF3340'],
    'MIL': ['#12284B', '#FFC52F'], 'MIN': ['#002B5C', '#D31145'], 'NYM': ['#002D72', '#FF5910'],
    'NYY': ['#003087', '#0C2340'], 'OAK': ['#003831', '#EFB21E'], 'PHI': ['#E81828', '#002D72'],
    'PIT': ['#27251F', '#FDB827'], 'SDP': ['#2F241D', '#FFC425'], 'SFG': ['#FD5A1E', '#27251F'],
    'SEA': ['#0C2C56', '#005C5C'], 'STL': ['#C41E3A', '#FEDB00'], 'TBR': ['#092C5C', '#8FBCE6'],
    'TEX': ['#003278', '#C0111F'], 'TOR': ['#134A8E', '#1D2D5C'], 'WSN': ['#AB0003', '#14225A']
}
def fetch_player_data(year, stat_type='batting', method='Standard'):
    if method == 'Standard':
        if stat_type == 'batting':
            return batting_stats(year)
        elif stat_type == 'pitching':
            return pitching_stats(year)
    elif method == 'Qual 0':
        # Use qual=0 parameter on the existing functions
        if stat_type == 'batting':
            return batting_stats(year, qual=0)
        elif stat_type == 'pitching':
            return pitching_stats(year, qual=0)
    raise ValueError("Invalid stat_type or method specified. Use 'batting' or 'pitching' with methods 'Standard' or 'Qual 0'.")

# Radio button for selecting the type of statistics
stat_type_selector = pn.widgets.RadioButtonGroup(
    name='Statistic Type', options=['batting', 'pitching']
)
# Radio button to toggle name labels
label_display_selector = pn.widgets.RadioButtonGroup(
    name='Label Display', options=['Hover', 'Always'], value='Hover'
)

# Radio button to toggle the data fetching method
data_method_selector = pn.widgets.RadioButtonGroup(
    name='Data Method', options=['Standard', 'Qual 0'], value='Standard'
)


# Dropdown menus for selecting the X and Y statistics
x_stat_selector = pn.widgets.Select(name='X-Axis Statistic')
y_stat_selector = pn.widgets.Select(name='Y-Axis Statistic')

# Slider for selecting the dot size
dot_size_slider = pn.widgets.IntSlider(name='Dot Size', start=5, end=15, step=1, value=8)

# Fetch initial data and set dropdown options
initial_data = fetch_player_data(2024, 'batting')
x_stat_selector.options = list(initial_data.columns)
y_stat_selector.options = list(initial_data.columns)
def create_scatter_plot(data, x_stat, y_stat, marker_size, label_display):
    if x_stat not in data.columns or y_stat not in data.columns:
        return go.Figure()

    traces = []
    for team, abbreviation in team_map.items():
        team_data = data[data['Team'] == abbreviation]
        if not team_data.empty:
            # Prepare text for hover or always on display
            text_for_display = [f"{row['Name']} - {row[x_stat]} {x_stat}, {row[y_stat]} {y_stat}" for index, row in team_data.iterrows()]
            text_always = [row['Name'] for index, row in team_data.iterrows()]

            traces.append(go.Scatter(
                x=team_data[x_stat],
                y=team_data[y_stat],
                mode='markers+text' if label_display == 'Always' else 'markers',
                marker=dict(size=marker_size, color=team_colors[abbreviation][0]),
                text=text_always if label_display == 'Always' else text_for_display,
                textposition='top center',
                hoverinfo='text' if label_display == 'Hover' else 'none',
                name=team  # Added to ensure each team trace can be distinguished in legend if needed
            ))

    layout = go.Layout(
        title=f"{x_stat} vs {y_stat}",
        xaxis=dict(title=x_stat),
        yaxis=dict(title=y_stat),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='white'),
        showlegend=False,  # Optionally show the legend
        legend=dict(x=1.02, y=1, orientation='v')
    )
    return go.Figure(data=traces, layout=layout)




@pn.depends(
    x_stat_selector.param.value, y_stat_selector.param.value,
    stat_type_selector.param.value, dot_size_slider.param.value,
    label_display_selector.param.value, data_method_selector.param.value
)
def update_plot(x_stat, y_stat, stat_type, marker_size, label_display, data_method):
    data = fetch_player_data(2024, stat_type, data_method)
    return create_scatter_plot(data, x_stat, y_stat, marker_size, label_display)

@pn.depends(stat_type_selector.param.value, watch=True)
def update_stat_options(stat_type):
    data = fetch_player_data(2024, stat_type)
    x_stat_selector.options = list(data.columns)
    y_stat_selector.options = list(data.columns)

dashboard = pn.template.MaterialTemplate(title="Team Performance Dashboard", header_background="#3f51b5", theme='dark')
dashboard.header.append(pn.Row(stat_type_selector, x_stat_selector, y_stat_selector, dot_size_slider))
dashboard.header.append(pn.Row(label_display_selector, data_method_selector))


dashboard.main.append(pn.pane.Plotly(update_plot, sizing_mode='stretch_both'))
# Custom CSS to style the dropdown text
custom_css = '''
    select.bk-input {
        color: black !important;
        background-color: white !important;
    }
    select.bk-input option {
        color: black !important;
        background-color: white !important;
    }
'''
# Add the custom CSS to the Panel configuration
pn.config.raw_css.append(custom_css)

app = dashboard.servable()

if __name__ == "__main__":
    pn.serve(app, address="0.0.0.0", port=8000)
