from src.util import make_example_data
import iesopt
import pandas as pd


data = make_example_data()

model = iesopt.run(
    "opt/config.iesopt.yaml",
    config={"optimization.snapshots.count": 96},
    parameters=dict(battery_soc_t0=100, grid_p_peak_consume=100),
    virtual_files=dict(data=data),
)

# Prepare model internal information.
snapshots = model.internal.model.snapshots
battery_state_lb = iesopt.IESopt.access(model.get_component("battery_storage").state_lb)
battery_state_ub = iesopt.IESopt.access(model.get_component("battery_storage").state_ub)

# Extract results.
results = model.results.to_pandas()

# Filter, prepare fullnames, and restore original times.
results = results.loc[(results["mode"] == "primal") & ~results["snapshot"].isnull()]
results["entry"] = results[["component", "fieldtype", "field"]].agg(".".join, axis=1)
t_map = dict(zip([snapshots[t + 1].name for t in range(len(snapshots))], data["time"]))
results["time"] = results["snapshot"].apply(lambda t: t_map[t])

# Pivot results to wide format.
results = results.pivot(index="time", columns="entry", values="value")

# Return selected results.
pd.DataFrame(
    {
        "schedule": results["market_da_buy.exp.value"] - results["market_da_sell.exp.value"],
        "battery_setpoint": (
            results["battery_discharging.exp.out_electricity"] - results["battery_charging.exp.in_electricity"]
        ),
        "battery_soc": (
            (results["battery_storage.var.state"] - battery_state_lb) / (battery_state_ub - battery_state_lb)
        ),
    }
)
