import iesopt


def make_example_data():
    """Returns a full day (24 hours as 96x 15 minutes) of example data for the day-ahead scheduling model.
    
    The data includes:
    - Timestamps in 15-minute intervals
    - PV generation (small and large)
    - Demand (small, large, and general)
    - Day-ahead price data

    Returns:
        pd.DataFrame: DataFrame with columns `time`, `pv_s`, `pv_l`, `demand_s`, `demand_l`, `demand_g`, and `price`.
    """
    rng = np.random.default_rng(seed=42)
    return pd.DataFrame(
        {
            "time": pd.date_range(start="2025-06-02 00:00", end="2025-06-02 23:45", freq="15min", tz="Europe/Vienna"),
            "pv_s": rng.uniform(0, 330, 96),
            "pv_l": rng.uniform(0, 1110, 96),
            "demand_s": rng.uniform(50, 300, 96),
            "demand_l": rng.uniform(0, 600, 96),
            "demand_g": rng.uniform(0, 150, 96),
            "price": rng.uniform(0.02, 0.15, 96),
        }
    )


def pivot_and_clean_results(model: iesopt.Model, ):
    # Extract results.
    snapshots = model.internal.model.snapshots
    results = model.results.to_pandas()

    # Filter, prepare fullnames, and restore original times.
    results = results.loc[(results["mode"] == "primal") & ~results["snapshot"].isnull()]
    results["entry"] = results[["component", "fieldtype", "field"]].agg(".".join, axis=1)
    t_map = dict(zip([snapshots[t + 1].name for t in range(len(snapshots))], data["time"]))
    results["time"] = results["snapshot"].apply(lambda t: t_map[t])

    # Pivot results to wide format.
    return results.pivot(index="time", columns="entry", values="value")

