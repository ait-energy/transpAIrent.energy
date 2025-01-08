import requests
from requests.auth import HTTPBasicAuth
import json
import dotenv
import pandas as pd
import iesopt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ╭─────────────────────────────────────────────────────────────────────────────────────────────────╮
# │ LOAD PRICE DATA FROM STROMPOOL MANAGER                                                          │
# ╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

try:
    with open("opt/files/strompool_request_prices.json", "r") as f:
        print("Using cached prices")
        data = json.load(f)
except FileNotFoundError:
    print("Fetching prices from Strompool API")

    url = dotenv.get_key(".env", "SP_URL")
    username = dotenv.get_key(".env", "SP_USER")
    password = dotenv.get_key(".env", "SP_PW")

    ret = requests.get(
        f"{url}/query/spotpreis/1?ab=2024-01-01&count=2880",
        auth=HTTPBasicAuth(username, password),
    )
    data = ret.json()
    with open("strompool_request_prices.json", "w") as f:
        json.dump(data, f)

# ╭─────────────────────────────────────────────────────────────────────────────────────────────────╮
# │ RESAMPLE PV DATA FOR LOCATION, CREATE IESopt INPUT FILE                                         │
# ╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

df = pd.read_csv(
    "opt/files/Timeseries_47.516_16.368_SA3_1kWp_crystSi_14_20deg_0deg_2023_2023.csv",
    index_col=0,
    parse_dates=True,
)
df.index = pd.to_datetime(df.index, format="%Y%m%d:%H%M")
df.index = df.index.map(lambda t: t.replace(minute=0))
df_resampled = df.resample("15min").interpolate()
df_resampled = df_resampled[["P"]]
df_resampled /= 1000.0
df_resampled = df_resampled.iloc[: (24 * 4 * 30)]
df_resampled["da_price"] = [float(it["preis"].replace(",", ".")) / 1000.0 for it in data]
df_resampled.to_csv("opt/files/data.csv")

df_heat_elec = pd.read_csv("opt/files/transpAIrent_heat_elec.csv", index_col=0, parse_dates=True)
df_heat_elec["heat"] = 0.7 * df_heat_elec["heat"].mean() + 0.3 * df_heat_elec["heat"]
df_heat_elec["elec"] = 0.5 * df_heat_elec["elec"].mean() + 0.5 * df_heat_elec["elec"]
df_heat_elec.clip(0.10).describe()
df_heat_elec.to_csv("opt/files/heat_elec.csv")

# ╭─────────────────────────────────────────────────────────────────────────────────────────────────╮
# │ RUN MODEL & VISUALIZE RESULTS                                                                   │
# ╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

cfg = "opt/config.iesopt.yaml"
T = list(range(2 * 24 * 4))
prices = df_resampled["da_price"].iloc[T]

runs = [
    iesopt.run(cfg, parameters=dict(heat_scale=1.0)),
    iesopt.run(cfg, parameters=dict(heat_scale=1.0, biogas_storage_lb=0.25)),
    iesopt.run(cfg, parameters=dict(heat_scale=2.0)),
    iesopt.run(cfg, parameters=dict(heat_scale=2.0, fixed_gas_mix=False)),
    iesopt.run(cfg, parameters=dict(heat_scale=1.0, battery=100)),
]
run_names = ["Base Case", "25% Min Storage", "2x Heat", "2x Heat + Varying Methane", "100 kWh Battery"]
run_colors = ["#006400", "#0000FF", "#FF0000", "#800080", "#FF8C38"]

base_cost = runs[0].objective_value
for run, name in zip(runs[1:], run_names[1:]):
    relative_cost = ((run.objective_value - base_cost) / base_cost) * 100
    print(f"Relative cost for {name}: {relative_cost:.2f}%")

fig = make_subplots(rows=2, cols=1, row_heights=[0.75, 0.25], shared_xaxes=True, vertical_spacing=0.05)
for (run, name, color) in zip(runs, run_names, run_colors):
    fig.add_trace(
        go.Scatter(
            x=T,
            y=run.results.components["biogas_storage"].var.state[T],
            name=name,
            line=dict(color=color, shape="spline"),
            mode="lines",
        ),
        row=1,
        col=1,
    )

max_bss = max(float(r.data.input.parameters["biogas_storage_size"]) for r in runs)
min_bss = min(float(r.data.input.parameters["biogas_storage_size"]) * float(r.data.input.parameters["biogas_storage_lb"]) for r in runs)
fig.add_trace(go.Bar(x=T, y=prices, name="Price", marker_color="#FF8C38"), row=2, col=1).update_layout(
    barmode="group", height=800, xaxis_title="Time", yaxis_title="Biogas Storage [kWh]", yaxis2_title="Price [€/kWh]",
    yaxis=dict(range=[min_bss * 0.5, max_bss * 1.10])
).show()
