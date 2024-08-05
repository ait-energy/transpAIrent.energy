# Chart API

Description of the chart API.

## Structure

The chart configuration is based on a configuration as specified below. To allow a easy usage via URL (GET) parameters, the (nested) configuration is passed as base64 encoded string. An exemplary encoded configuration is:

```text
ewogICAgInR5cGUiOiAiYmFyK3N0YWNrZWQiLAogICAgIm9wdGlvbnMiOiB7CiAgICAgICAgInRpdGxlIjogbnVsbCwKICAgICAgICAidW5pdCI6ICJNVyIsCiAgICAgICAgInRpbWUiOiB7CiAgICAgICAgICAgICJyYW5nZSI6ICJjdXJyZW50ZGF5IiwKICAgICAgICAgICAgInJlc29sdXRpb24iOiAib3JpZ2luYWwiCiAgICAgICAgfSwKICAgICAgICAiYXNwZWN0IjogIndpZGUiLAogICAgICAgICJheGVzIjogeyJ4IjogeyJsYWJlbCI6ICJfX0RFRkFVTFRfXyJ9LCAieSI6IHsibGFiZWwiOiAiRXJ6ZXVndW5nIFtNV10ifX0sCiAgICAgICAgImxlZ2VuZCI6IHsKICAgICAgICAgICAgInBvc2l0aW9uIjogInRvcCIKICAgICAgICB9LAogICAgICAgICJsaW5rcyI6IHsKICAgICAgICAgICAgInJlYWRtb3JlIjogImh0dHBzOi8vdHJhbnNwYWlyZW50LmVuZXJneS9jb21wZW5kaXVtL2VyemV1Z3VuZ3NtaXgiCiAgICAgICAgfQogICAgfSwKICAgICJ0cmFjZXMiOiBbCiAgICAgICAgewogICAgICAgICAgICAiZmVhdHVyZSI6ICJoaXN0b3JpYy9kYV9lbnRzb2Uvd2luZCIsCiAgICAgICAgICAgICJjb2xvciI6ICIjZmYwMDAwIiwKICAgICAgICAgICAgImxhYmVsIjogIldpbmQiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAgICJmZWF0dXJlIjogImhpc3RvcmljL2RhX2VudHNvZS9zb2xhcl9wdl9hY3QiLAogICAgICAgICAgICAiY29sb3IiOiAiIzAwZmYwMCIsCiAgICAgICAgICAgICJsYWJlbCI6ICJQaG90b3ZvbHRhaWsiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAgICJmZWF0dXJlIjogImhpc3RvcmljL2RhX2VudHNvZS9vdGhlciIsCiAgICAgICAgICAgICJjb2xvciI6ICIjNDI0MjQyIiwKICAgICAgICAgICAgImxhYmVsIjogIkFuZGVyZSIKICAgICAgICB9CiAgICBdLAogICAgIm92ZXJsYXlzIjogWwogICAgICAgIHsKICAgICAgICAgICAgInR5cGUiOiAiZmVhdHVyZSIsCiAgICAgICAgICAgICJkYXRhIjogewogICAgICAgICAgICAgICAgImZlYXR1cmUiOiAiaGlzdG9yaWMvYXBnL2RlbWFuZCIsCiAgICAgICAgICAgICAgICAiY29sb3IiOiAiI2YwMDAwMCIsCiAgICAgICAgICAgICAgICAid2lkdGgiOiAicmVndWxhciIsCiAgICAgICAgICAgICAgICAibGFiZWwiOiAiTmFjaGZyYWdlIgogICAgICAgICAgICB9CiAgICAgICAgfQogICAgXQp9
```

### Top level

```json
{
    // General specification of the chart type.
    "type": "...",
    // General options, configuring chart title, legend, ...
    "options": {},
    // List of traces (order matters for stacked charts).
    "traces": [],
    // List of overlays, similar to traces (order matters).
    "overlays": []
}
```

### `type`

General type of the chart. Base type, e.g., `bar` or `line`, in combination with various modifiers, e.g., `stacked`, which are separated by `+`.

> **Type:**
> `string`

> **Values:**
> Given in the form of `base+modifierA+modifierB`.
> - *base:* `bar`, `line`
> - *modifiers:* `stacked`, `grouped`

> **Example:** `bar+stacked`

### `options`

General options that configure the overall chart. All entries are mandatory, passing `null` disables the respective functionality.

```json
"options": {
    /* Title (top) of the chart.
     * ~~~ Either a `string` or `null`.
     * ~~~ If `null` is passed, the title is not displayed. Passing "" (an empty
     * ~~~ string) does not hide the title, but leaves it empty.
     */
    "title": "...",

    /* Unit of the features.
     * ~~~ Only used as validation of the configuration.
     */
    "unit": "MW",
    
    /* Initial timerange and -resolution selector.
     * ~~~ Range, either:
     * ~~~    one of: "currentday", "currentweek", "currentmonth", "currentyear"
     * ~~~    or: ["timefrom", "timeto"]
     * ~~~ For the list based range, the second entry is inclusive.
     *
     * ~~~ Resolution, one of:
     * ~~~    "original", showing the raw data
     * ~~~    "1H", "4H", "1D", "1W", "1M", for resampled (mean) values
     * ~~~    "avg1H", "avgWD", for average values per group
     */
    "time": {
        "range": "currentday",
        "resolution": "original"
    },
    
    /* Aspect ratio of the chart, inteded as information.
     * ~~~ One of: "wide", "square"
     */
    "aspect": "wide",

    /* Configuration of x- and y-axis.
     * ~~~ Contains:
     * ~~~    label: either a `string` or "__DEFAULT__"
     * ~~~ If "__DEFAULT__", the label is chosen by the backend. For example,
     * ~~~ for any chart using a time-based x-axis, the label could be
     * ~~~ "Zeitpunkt" or, e.g., "Wochentag" if aggregated by day of the week.
     * ~~~ This is dynamically chosen, and can therefore not be set.
     */
    "axes": {
        "x": {"label": "__DEFAULT__"},  // `string` or `"__DEFAULT__"`
        "y": {"label": "Erzeugung"}     // `string` or `"__DEFAULT__"`
    },

    /* Configuration of the legend.
     * ~~~ Contains:
     * ~~~    position: "top", "bottom", "right", "left"
     * ~~~ Passing `legend: null` disables and hides the legend.
     */
    "legend": {
        "position": "top"    // one of: top, bottom, right, left
    },

    /* Configures link targets for embedded links.
     * ~~~ Options:
     * ~~~    readmore, the link embedded "Mehr Informationen", containing more
     * ~~~              background information related to the current chart.
     */
    "links": {
        "readmore": "https://transpairent.energy/compendium/erzeugungsmix"
    }
}
```

### `traces`

Adds one or multiple traces to the chart. All selected features must have the same unit, that has to be identical to the one given in the `options` entry. `traces` is a list of traces, where the order matters for charts that require an order (e.g., stacked bar charts).

```json
"traces": [
    {
        // Selector (= path) to the feature.
        "feature": "historic/da_entsoe/wind",
        // Color of the trace, hex coded. Optional alpha channel.
        "color": "#ff0000",
        // Human readable name (for tooltip and legend).
        "label": "Wind"
    }
]
```

A chart of type `line` also allows:

- `width`: any `float`, or "regular" (default)
- `dashed`: `true` or `false` (default)
- `mode`: `lininterp` (default) for linear interpolation, or `stepped`
- `markers`: `true` (default) or `false`, to control showing (circle) markers

### `overlays`

Similar to traces, but limited to specific use-cases. Overlays are always displayed as line trace, no matter the current chart type.

```json
"overlays": [
    {
        // Type of the overlay, either "feature" or "ruler".
        "type": "feature",
        // Data, identical to how traces are configured.
        "data": {
            "feature": "historic/apg/demand",
            "color": "#f00000",
            "width": "regular",
            "label": "Nachfrage"
        }
    },
    {
        "type": "ruler",
        "data": {
            "value": 100.0,
            "color": "#f00000",
            "width": 1,
            "dashed": true,
            "label": "100"
        }
    },
    {
        "type": "ruler",
        "data": {
            "value": "avg_currentyear", // compare: timerange selector
            "color": "#00aa33",
            "width": 3,
            "label": "Durchschnittswert"
        }
    },
]
```
