# oceannetworks_data

Python toolset for programmatic access to [Ocean Networks Canada (ONC)](https://www.oceannetworks.ca/) cabled observatory data via the [Oceans 3.0 API](https://data.oceannetworks.ca/OpenAPI).

---

## Overview

Utilities for spatial discovery, deployment reconnaissance, and bulk download of scalar time-series data from ONC's NEPTUNE and VENUS cabled observatories. Data is saved as NetCDF4 files with deployment metadata preserved as global attributes.

---

## Requirements

- [pixi](https://pixi.sh) (manages the conda/pip environment via `pixi.toml`)

---

## Installation

```bash
git clone https://github.com/dksasaki/oceannetworks_data.git
cd oceannetworks_data
pixi install
```

---

## Authentication

Store your [Oceans 3.0 API token](https://data.oceannetworks.ca) in a `.login` file at the project root:

```bash
echo "your-token-here" > .login
echo ".login" >> .gitignore
```

The token is resolved via `PIXI_PROJECT_ROOT`:

```python
token_file = os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")
```

---

## API

### `get_onc()`

Instantiates and returns an authenticated `ONC` client.

---

### `recon_device(onc, device_category, lat_min, lat_max, lon_min, lon_max)`

Queries deployments for a given `deviceCategoryCode` within a bounding box. For each deployment, retrieves location metadata, available properties, and deployment time bounds. Prints download-ready parameters and returns a list of deployment dicts.

**Returns:** `list[dict]` with keys:

| Key | Description |
|-----|-------------|
| `locationCode` | ONC location identifier |
| `deviceCategoryCode` | Device category |
| `lat`, `lon` | Deployment coordinates |
| `depth` | Water depth (m) |
| `begin`, `end` | Deployment time bounds (ISO8601 UTC) |
| `propertyCodes` | List of available property codes |

---

### `download_devices(onc, devices_list, output_dir="data")`

Downloads scalar time-series for each deployment in `devices_list` via `getDirectByLocation`. Each property is saved as an independent NetCDF4 file.

Decorated with `@check_downloaded` — skips properties for which a matching file already exists in `output_dir`, enabling incremental downloads.

**File naming:**

```
{locationCode}_{propertyCode}_{tStart}_{tEnd}.nc
```

**NetCDF global attributes:** `locationCode`, `deviceCategoryCode`, `lat`, `lon`, `depth`

---

### `check_downloaded(output_dir)`

Decorator for `download_devices`. Before downloading, checks `output_dir` for files matching `{locationCode}_{propertyCode}_*`. Narrows `propertyCodes` in each deployment dict to only missing properties. Skips the download entirely if all properties are present.

---

## Workflow

### Step 1 — Connect and load all deployments

```python
from onc_tools import get_onc, recon_device, download_devices
import pandas as pd

onc = get_onc()
deployments = onc.getDeployments({})
df = pd.DataFrame(deployments)
```

### Step 2 — Define bounding box and filter deployments

```python
lat_min, lat_max = 48.09945106423486, 48.57934033063693
lon_min, lon_max = -126.33077903027713, -125.5997327646366

mask = (
    df["lat"].notna() & df["lon"].notna() &
    df["lat"].between(lat_min, lat_max) &
    df["lon"].between(lon_min, lon_max)
)
df = df[mask]
```

### Step 3 — Select a device category code

Enumerate what is available in the bounding box:

```python
print(set(df["deviceCategoryCode"]))
```

Pick a code from the output (see [Device Category Codes](#device-category-codes) for reference) and check how many deployments exist:

```python
code = "OXYSENSOR"
deployments_bydeviceCategoryCode(onc, code, df, lat_min, lat_max, lon_min, lon_max)
```

### Step 4 — Reconnaissance

Inspect deployment details, available properties, and time bounds for the selected code:

```python
devices_list = recon_device(onc, code, lat_min, lat_max, lon_min, lon_max)
```

Example output:

```
=== OXYSENSOR | 3 deployments ===

-- BACAX | lat=48.3118, lon=-126.0652, depth=860.5 --
   begin=2016-05-14T03:38:34.000Z, end=2017-06-20T19:54:58.000Z
   download params:
     locationCode       = 'BACAX'
     deviceCategoryCode = 'OXYSENSOR'
     propertyCode       = ['oxygen', 'seawatertemperature']
     dateFrom           = '2016-05-14T03:38:34.000Z'
     dateTo             = '2017-06-20T19:54:58.000Z'
```

### Step 5 — Download

```python
bla = download_devices(onc, devices_list, output_dir="data")
```

Each property is saved as an independent NetCDF4 file. Already-downloaded properties are skipped automatically.

---

## Device Category Codes

Relevant codes for bottom water column and sediment measurements:

| Code | Instrument |
|------|-----------|
| `CTD` | Temperature, salinity, pressure |
| `OXYSENSOR` | Dissolved oxygen |
| `CTDPHOX` | CTD + oxygen + pH |
| `CO2SENSOR` | pCO2 |
| `NITRATESENSOR` | Nitrate |
| `GTD` | Dissolved gas (methane, total gas) |
| `CHEMINI` | Fe, nutrients at sediment-water interface |
| `BPR` | Bottom pressure recorder (tsunamis, tectonics) |
| `CORK` | Sub-seafloor borehole pressure and temperature |
| `TURBIDITY` | Turbidity |
| `FLUOROMETER` | Chlorophyll, CDOM |

---

## Notes

- Deployments with `begin=None` or `end=NaN` are skipped. Active deployments (no `end`) can be handled by substituting `pd.Timestamp.utcnow()`.
- `getDirectByLocation` returns all properties for a location/deviceCategory in a single call; filtering is applied post-response via `propertyCodes`.
- Time indices are stripped of UTC timezone info (`tz_localize(None)`) prior to NetCDF serialization.
- NetCDF4 engine is required to avoid int32 overflow on nanosecond-resolution time arrays.
- The ONC API enforces rate limits — avoid multithreaded requests.

---

## References

- Oceans 3.0 API: https://data.oceannetworks.ca/OpenAPI
- Python client: https://oceannetworkscanada.github.io/api-python-client
- API guide: https://oceannetworkscanada.github.io/Oceans3.0-API