import os
from onc import ONC
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import cartopy.feature as cfeature
import xarray as xr


# ==============================================================================
# UTILITIES
# ==============================================================================

def print_key_tree(d, indent=0):
    """Recursively print the keys of a nested dictionary."""
    for key, value in d.items():
        print("  " * indent + str(key))
        if isinstance(value, dict):
            print_key_tree(value, indent + 1)


def get_onc():
    """
    Instantiate the ONC client using a token stored in a .login file.
    The file path is resolved relative to the PIXI_PROJECT_ROOT environment variable.

    Returns
    -------
    ONC
        Authenticated ONC client instance.
    """
    token_file = os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")
    with open(token_file) as f:
        token = f.read().strip()
    return ONC(token=token)


# ==============================================================================
# MAPS
# ==============================================================================

def get_oxygen_maps(df):
    """
    Plot locations of oxygen-related sensors on a map.

    Groups sensors into: CTD+ODO (by deviceCode), OXYSENSOR, CTDPHOX, GTD, WETLABS_WQM.

    Parameters
    ----------
    df : pd.DataFrame
        Deployments dataframe containing columns: deviceCode, deviceCategoryCode, lat, lon.
    """
    sensor_groups = {
        'CTD+ODO (deviceCode)': df['deviceCode'].str.contains('ODO', na=False) | df['deviceCode'].str.contains('RBRCONCERTO', na=False),
        'OXYSENSOR':            df['deviceCategoryCode'] == 'OXYSENSOR',
        'CTDPHOX':              df['deviceCategoryCode'] == 'CTDPHOX',
        'GTD':                  df['deviceCategoryCode'] == 'GTD',
        'WETLABS_WQM':          df['deviceCategoryCode'] == 'WETLABS_WQM',
    }
    styles = {
        'CTD+ODO (deviceCode)': dict(s=15),
        'OXYSENSOR':            dict(s=5),
        'CTDPHOX':              dict(marker='x', c='r'),
        'GTD':                  dict(marker='*', c='c', alpha=0.5),
        'WETLABS_WQM':          dict(marker=',', c='m', alpha=0.5),
    }
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={"projection": ccrs.PlateCarree()})
    ax.coastlines(resolution='10m', linewidth=1)
    for label, mask in sensor_groups.items():
        pts = df[mask][['lat', 'lon']].drop_duplicates()
        ax.scatter(pts['lon'], pts['lat'], label=label, **styles[label])
    ax.legend(loc='lower left', fontsize=8)
    plt.title("Oxygen Sensors")
    plt.tight_layout()
    plt.show()




# ==============================================================================
# DISCOVERY
# ==============================================================================

def deployments_bydeviceCategoryCode(onc, code, df, lat_min, lat_max, lon_min, lon_max):
    """
    Print the number of deployments for a given device category code within a bounding box.

    Parameters
    ----------
    onc : ONC
        Authenticated ONC client instance.
    code : str
        Device category code (e.g. 'OXYSENSOR').
    df : pd.DataFrame
        Deployments dataframe already filtered to the bounding box.
    lat_min, lat_max, lon_min, lon_max : float
        Bounding box coordinates.
    """
    deps = onc.getDeployments({"deviceCategoryCode": code})
    df_dep = pd.DataFrame(deps)
    if df_dep.empty:
        return
    mask = (
        df_dep["lat"].notna() & df_dep["lon"].notna() &
        df_dep["lat"].between(lat_min, lat_max) &
        df_dep["lon"].between(lon_min, lon_max)
    )
    n = mask.sum()
    if n > 0:
        print(code, n)


def recon_device(onc, device_category, lat_min, lat_max, lon_min, lon_max):
    """
    Discover deployments for a device category within a bounding box and print
    the parameters needed to download data for each deployment.

    Parameters
    ----------
    onc : ONC
        Authenticated ONC client instance.
    device_category : str
        Device category code (e.g. 'CTD', 'OXYSENSOR').
    lat_min, lat_max, lon_min, lon_max : float
        Bounding box coordinates in decimal degrees.

    Returns
    -------
    list of dict
        Each dict contains locationCode, deviceCategoryCode, lat, lon, depth,
        begin, end, and propertyCodes for one deployment.
    """
    deps = onc.getDeployments({"deviceCategoryCode": device_category})
    df_dep = pd.DataFrame(deps)
    if df_dep.empty:
        print(f"{device_category}: no deployments found")
        return []

    mask = (
        df_dep["lat"].notna() & df_dep["lon"].notna() &
        df_dep["lat"].between(lat_min, lat_max) &
        df_dep["lon"].between(lon_min, lon_max)
    )
    df_dep = df_dep[mask]

    if df_dep.empty:
        print(f"{device_category}: no deployments in bbox")
        return []

    print(f"=== {device_category} | {len(df_dep)} deployments ===")

    results = []
    for _, row in df_dep.iterrows():
        lcode = row["locationCode"]
        props = onc.getProperties({"locationCode": lcode, "deviceCategoryCode": device_category})
        prop_codes = [p["propertyCode"] for p in props]
        loc = onc.getLocations({"locationCode": lcode})
        depth = loc[0].get("depth") if loc else None

        print(f"\n-- {lcode} | lat={row['lat']:.4f}, lon={row['lon']:.4f}, depth={depth} --")
        print(f"   begin={row.get('begin')}, end={row.get('end')}")
        print(f"   download params:")
        print(f"     locationCode       = '{lcode}'")
        print(f"     deviceCategoryCode = '{device_category}'")
        print(f"     propertyCode       = {prop_codes}  # pick one or omit for all")
        print(f"     dateFrom           = '{row.get('begin')}'")
        print(f"     dateTo             = '{row.get('end')}'")

        results.append({
            "locationCode":       lcode,
            "deviceCategoryCode": device_category,
            "lat":                row["lat"],
            "lon":                row["lon"],
            "depth":              depth,
            "begin":              row.get("begin"),
            "end":                row.get("end"),
            "propertyCodes":      prop_codes,
        })

    return results


# ==============================================================================
# DOWNLOAD
# ==============================================================================

def download_devices(onc, devices_list, output_dir="data"):
    """
    Download scalar data for a list of devices and save each property as a
    separate NetCDF file.

    File naming convention: {locationCode}_{propertyCode}_{tStart}_{tEnd}.nc

    Parameters
    ----------
    onc : ONC
        Authenticated ONC client instance.
    devices_list : list of dict
        Output of recon_device — each dict describes one deployment.
    output_dir : str
        Directory where NetCDF files are saved. Created if it doesn't exist.

    Returns
    -------
    dict
        Nested dict: {locationCode: {lon, lat, depth, df: {propertyCode: pd.DataFrame}}}
    """
    os.makedirs(output_dir, exist_ok=True)
    bla = {}

    for device in devices_list:
        date_from = device.get("begin")
        date_to   = device.get("end")

        # skip deployments with missing or NaN time bounds
        if not date_from or not date_to or pd.isna(date_to):
            print(f"  {device['locationCode']}: skipping, no time range")
            continue

        data = onc.getDirectByLocation({
            "locationCode":       device["locationCode"],
            "deviceCategoryCode": device["deviceCategoryCode"],
            "dateFrom":           date_from,
            "dateTo":             date_to,
        })

        lcode = device["locationCode"]
        bla[lcode] = {"lon": device["lon"], "lat": device["lat"], "depth": device["depth"], "df": {}}

        for data0 in data["sensorData"]:
            prop = data0["propertyCode"]
            t    = data0["data"]["sampleTimes"]
            v    = data0["data"]["values"]

            df_sensor = pd.DataFrame(index=t, data=v, columns=[prop])
            df_sensor.index = pd.to_datetime(df_sensor.index)
            df_sensor = df_sensor.dropna()
            df_sensor.index = df_sensor.index.tz_localize(None)  # strip UTC for NetCDF compatibility

            bla[lcode]["df"][prop] = df_sensor

            ds = xr.Dataset(
                {prop: ("time", df_sensor[prop].values)},
                coords={"time": df_sensor.index},
                attrs={
                    "locationCode":       lcode,
                    "deviceCategoryCode": device["deviceCategoryCode"],
                    "lat":                device["lat"],
                    "lon":                device["lon"],
                    "depth":              device["depth"],
                }
            )

            t_start = df_sensor.index[0].strftime("%Y%m%dT%H%M%S")
            t_end   = df_sensor.index[-1].strftime("%Y%m%dT%H%M%S")
            fname   = f"{lcode}_{prop}_{t_start}_{t_end}.nc"
            ds.to_netcdf(os.path.join(output_dir, fname))
            print(f"saved: {fname}")

    return bla


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    """
    Workflow:
        1) Connect to the ONC database
        2) Define a bounding box and filter deployments
        3) Select a device category code
        4) Discover deployments with recon_device
        5) Download and save data as NetCDF
    """

    # -- 1) connect -- #
    onc = get_onc()
    deployments = onc.getDeployments({})

    # -- 2) bounding box -- #
    lat_min, lat_max = 48.09945106423486, 48.57934033063693
    lon_min, lon_max = -126.33077903027713, -125.5997327646366

    df = pd.DataFrame(deployments)
    mask = (
        df["lat"].notna() & df["lon"].notna() &
        df["lat"].between(lat_min, lat_max) &
        df["lon"].between(lon_min, lon_max)
    )
    df = df[mask]

    # -- 3) select device category -- #
    print(set(df['deviceCategoryCode']))
    code = "OXYSENSOR"

    deployments_bydeviceCategoryCode(onc, code, df, lat_min, lat_max, lon_min, lon_max)

    # -- 4) discover -- #
    devices_list = recon_device(onc, code, lat_min, lat_max, lon_min, lon_max)

    # -- 5) download -- #
    bla = download_devices(onc, devices_list, output_dir="data")