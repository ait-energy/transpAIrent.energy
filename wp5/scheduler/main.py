from src.util import make_example_data, normalize_to_eom
from src.scheduler import get_day_ahead_schedule

data = make_example_data()
data = normalize_to_eom(data)

schedule = get_day_ahead_schedule(data, battery_soc_t0=0.5, grid_p_peak_consume=100)
