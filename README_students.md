# oceannetworks_data

Python environment for downloading and exploring data from [Ocean Networks Canada (ONC)](https://www.oceannetworks.ca/) via the [Oceans 3.0 API](https://data.oceannetworks.ca/OpenAPI).

---

## Overview

This project provides a set of Python scripts to:

- Connect to the ONC database
- Search for instruments by location and type
- Download time-series data
- Save data as NetCDF files for further analysis

---

## Requirements

Before starting, you need to install the following tools on your computer:

| Tool | Purpose | Download |
|------|---------|----------|
| [Git](https://git-scm.com/downloads) | Download the project files | https://git-scm.com/downloads |
| [pixi](https://pixi.sh) | Manage the Python environment and dependencies | https://pixi.sh |

You do not need to install Python separately — pixi handles that for you.

---

## Step-by-Step Installation

### 1. Install Git

Download and install Git from https://git-scm.com/downloads. Follow the installer for your operating system (Windows, macOS, or Linux).

To verify Git is installed, open a terminal and run:

```bash
git --version
```

### 2. Install pixi

Open a terminal and run:

**macOS / Linux:**

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

**Windows (PowerShell):**

```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

To verify pixi is installed:

```bash
pixi --version
```

> **What is a terminal?**
> - On **macOS**: open Spotlight (Cmd+Space) and type "Terminal"
> - On **Windows**: search for "PowerShell" in the Start menu
> - On **Linux**: look for "Terminal" in your applications

### 3. Clone the repository

"Cloning" downloads the project files to your computer. In your terminal, navigate to where you want to store the project and run:

```bash
git clone https://github.com/dksasaki/oceannetworks_data.git
cd oceannetworks_data
```

> **Tip:** `cd` means "change directory" — it moves you into the project folder.

### 4. Install the Python environment

Inside the project folder, run:

```bash
pixi install
```

This automatically installs all required Python packages. This may take a few minutes the first time.

---

## ONC API Token

An API token is a personal key that identifies you when accessing ONC data. It is required to download any data.

### Obtaining a token

1. Register for a free account at https://data.oceannetworks.ca/Registration
2. Log in at https://data.oceannetworks.ca
3. Click **Profile** in the top right corner
4. Go to the **Web Services API** tab
5. Click **Copy Token**

Your token looks like this: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Storing the token

Create a file called `.login` at the root of the project folder and paste your token into it (nothing else, just the token):

**macOS / Linux:**

```bash
echo "your-token-here" > .login
```

**Windows (PowerShell):**

```powershell
"your-token-here" | Out-File -FilePath .login -Encoding ascii
```

Or simply open a text editor, paste your token, and save the file as `.login` in the project folder.

> **Important:** Never share your token. To prevent it from being accidentally uploaded to GitHub, add `.login` to your `.gitignore`:
>
> ```bash
> echo ".login" >> .gitignore
> ```

---

## Running the Scripts

### Launch an interactive session

The recommended way to explore the data interactively is via IPython:

```bash
pixi run ipython
```

This opens an interactive Python prompt where you can run commands one at a time.

### Basic example

```python
from onc_tools import get_onc, recon_device, download_devices

# connect to ONC
onc = get_onc()

# define a bounding box (lat_min, lat_max, lon_min, lon_max)
lat_min, lat_max = 48.09945106423486, 48.57934033063693
lon_min, lon_max = -126.33077903027713, -125.5997327646366

# discover oxygen sensor deployments in the bounding box
devices_list = recon_device(onc, "OXYSENSOR", lat_min, lat_max, lon_min, lon_max)

# download and save data as NetCDF files in the data/ folder
bla = download_devices(onc, devices_list, output_dir="data")
```

### What is a bounding box?

A bounding box defines a rectangular geographic area using minimum and maximum latitude and longitude values. Only instruments within this area will be returned.

```
lat_max  ┌─────────────┐
         │             │
         │   bbox      │
         │             │
lat_min  └─────────────┘
       lon_min        lon_max
```

### What is a NetCDF file?

NetCDF (`.nc`) is a standard scientific file format for storing time-series data alongside metadata (location, depth, units). It can be opened in Python (xarray, pandas), MATLAB, R, and many other tools.

---

## Workflow

The typical workflow follows these steps:

```
1. get_onc()
        │
        ▼
2. getDeployments()          ← list all instruments in the database
        │
        ▼
3. filter by bounding box    ← narrow down to your area of interest
        │
        ▼
4. recon_device()            ← inspect available properties and time ranges
        │
        ▼
5. download_devices()        ← download and save as NetCDF
```

### Available device category codes

Some common codes relevant for bottom water column and sediment measurements:

| Code | Instrument type |
|------|----------------|
| `CTD` | Temperature, salinity, pressure |
| `OXYSENSOR` | Dissolved oxygen |
| `CTDPHOX` | CTD with oxygen and pH |
| `CO2SENSOR` | Partial pressure of CO2 |
| `NITRATESENSOR` | Nitrate |
| `GTD` | Dissolved gas (e.g. methane) |
| `CHEMINI` | Iron, nutrients at sediment interface |
| `BPR` | Bottom pressure recorder |
| `CORK` | Sub-seafloor borehole pressure and temperature |
| `TURBIDITY` | Turbidity |
| `FLUOROMETER` | Chlorophyll, CDOM |

To see which codes are available in your bounding box:

```python
import pandas as pd
from onc_tools import get_onc

onc = get_onc()
deployments = onc.getDeployments({})
df = pd.DataFrame(deployments)

lat_min, lat_max = 48.09945106423486, 48.57934033063693
lon_min, lon_max = -126.33077903027713, -125.5997327646366

mask = (
    df["lat"].notna() & df["lon"].notna() &
    df["lat"].between(lat_min, lat_max) &
    df["lon"].between(lon_min, lon_max)
)

print(set(df[mask]["deviceCategoryCode"]))
```

---

## Output Files

Downloaded data is saved in the `data/` folder as NetCDF files, named as:

```
{locationCode}_{propertyCode}_{startTime}_{endTime}.nc
```

For example:

```
BACAX_oxygen_20240101T000000_20240102T000000.nc
```

Each file contains:

- The time series of the measured property
- Metadata: location code, device category, latitude, longitude, depth

To load a file in Python:

```python
import xarray as xr

ds = xr.open_dataset("data/BACAX_oxygen_20240101T000000_20240102T000000.nc")
print(ds)
```

To count how many files have been downloaded:

```bash
ls data/ | wc -l
```

---

## Project Structure

```
oceannetworks_data/
├── onc_tools.py       # main functions for discovery and download
├── pixi.toml          # environment definition (dependencies)
├── .login             # your ONC token (not shared, not uploaded)
├── data/              # downloaded NetCDF files (created automatically)
└── README.md          # this file
```

---

## Troubleshooting

**`PIXI_PROJECT_ROOT` not set**
Make sure you run scripts from inside the project folder using `pixi run`.

**Token error**
Double-check that `.login` contains only your token with no extra spaces or newlines.

**No data returned**
The bounding box or time range may not overlap with any deployments. Use `recon_device` to check what is available before downloading.

**`NoneType` error on download**
Some deployments have no data archived. The script will skip these automatically and print a warning.

**Package not found**
Re-run `pixi install` to ensure all dependencies are installed.

---

## References

- ONC Data Portal: https://data.oceannetworks.ca
- ONC API documentation: https://oceannetworkscanada.github.io/Oceans3.0-API
- Python client library: https://oceannetworkscanada.github.io/api-python-client
- NetCDF format: https://www.unidata.ucar.edu/software/netcdf