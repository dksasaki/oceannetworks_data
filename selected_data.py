import os
from onc import ONC
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import cartopy.feature as cfeature
import os


def print_key_tree(d, indent=0):
    for key, value in d.items():
        print("  " * indent + str(key))
        if isinstance(value, dict):
            print_key_tree(value, indent + 1)



def get_onc():
    token_file = os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")
    with open(token_file) as f:
        token = f.read().strip()

    onc = ONC(token=token)
    return onc




def get_oxygen_maps(df):
    sensor_groups = {
        'CTD+ODO (deviceCode)':    df['deviceCode'].str.contains('ODO', na=False) | df['deviceCode'].str.contains('RBRCONCERTO', na=False),
        'OXYSENSOR':               df['deviceCategoryCode'] == 'OXYSENSOR',
        'CTDPHOX':                 df['deviceCategoryCode'] == 'CTDPHOX',
        'GTD':                     df['deviceCategoryCode'] == 'GTD',
        'WETLABS_WQM':             df['deviceCategoryCode'] == 'WETLABS_WQM',
    }

    styles = {
        'CTD+ODO (deviceCode)':    dict(s=15),
        'OXYSENSOR':               dict(s=5),
        'CTDPHOX':                 dict(marker='x', c='r'),
        'GTD':                     dict(marker='*', c='c', alpha=0.5),
        'WETLABS_WQM':             dict(marker=',', c='m', alpha=0.5),
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

def get_oxygen_maps():

    sensors = ['CTD', ]
    odo_mask = df['deviceCode'].str.contains('ODO', na=False)
    rbr_mask = df['deviceCode'].str.contains('RBRCONCERTO', na=False)
    oxygen_mask = odo_mask | rbr_mask
    df_ctd_oxygen = df[oxygen_mask]
    df_no_duplicates = df_ctd_oxygen[['lat','lon']].drop_duplicates()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'],s=15)
    # ax.coastlines()


    sensors = ['OXYSENSOR', ]
    mask = df['deviceCategoryCode'].isin(sensors)
    df_filtered = df[mask]
    df_no_duplicates = df_filtered[['lat','lon']].drop_duplicates()
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'],s=5)
    ax.coastlines(resolution='10m',linewidth=1)



    sensors = ['CTDPHOX', ]
    mask = df['deviceCategoryCode'].isin(sensors)
    df_filtered = df[mask]
    df_no_duplicates = df_filtered[['lat','lon']].drop_duplicates()
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], marker='x', c='r')
    # ax.coastlines(resolution='10m')


    sensors = ['GTD', ]
    mask = df['deviceCategoryCode'].isin(sensors)
    df_filtered = df[mask]
    df_no_duplicates = df_filtered[['lat','lon']].drop_duplicates()
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], marker='*', c='c', alpha=0.5)
    # ax.coastlines(resolution='10m')

    sensors = ['WETLABS_WQM', ]
    mask = df['deviceCategoryCode'].isin(sensors)
    df_filtered = df[mask]
    df_no_duplicates = df_filtered[['lat','lon']].drop_duplicates()
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], marker=',', c='m', alpha=0.5)
    # ax.coastlines(resolution='10m')


def get_nitrate_maps():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # NITRATESENSOR by deviceCategoryCode
    mask = df['deviceCategoryCode'] == 'NITRATESENSOR'
    df_no_duplicates = df[mask][['lat', 'lon']].drop_duplicates()
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], s=15, label='NITRATESENSOR')

    # CHEMINI
    mask = df['deviceCategoryCode'] == 'CHEMINI'
    df_no_duplicates = df[mask][['lat', 'lon']].drop_duplicates()
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], s=15, marker='x', c='r', label='CHEMINI')

    # UWVOLTAMMETRICSYSTEM
    mask = df['deviceCategoryCode'] == 'UWVOLTAMMETRICSYSTEM'
    df_no_duplicates = df[mask][['lat', 'lon']].drop_duplicates()
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], s=15, marker='*', c='c', alpha=0.5, label='UWVOLTAMMETRIC')

    # WETLABS_WQM
    mask = df['deviceCategoryCode'] == 'WETLABS_WQM'
    df_no_duplicates = df[mask][['lat', 'lon']].drop_duplicates()
    ax.scatter(df_no_duplicates['lon'], df_no_duplicates['lat'], s=15, marker=',', c='m', alpha=0.5, label='WETLABS_WQM')

    ax.coastlines(resolution='10m', linewidth=1)
    ax.legend()
    plt.title("Nitrate Sensors")
    plt.show()

    
def deployments_bydeviceCategoryCode(code):    
    deps = onc.getDeployments({"deviceCategoryCode": code})
    df_dep = pd.DataFrame(deps)
    if df_dep.empty:
        return 0
    mask = (
        df_dep["lat"].notna() & df_dep["lon"].notna() &
        df_dep["lat"].between(lat_min, lat_max) &
        df_dep["lon"].between(lon_min, lon_max)
    )
    n = mask.sum()
    if n > 0:
        print(code, n)

def recon_device(onc, device_category, lat_min, lat_max, lon_min, lon_max):

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


if __name__ == '__main__':       
    """
    How to use this script

    1) access the database
    2) set the bounding box
    3) determine the device category code you are interested in

    """

    # -- 1) access database --- #
    onc = get_onc()
    deployments = onc.getDeployments({})

    # -- 2) define bounding box and mask data-- #
    lat_min, lat_max = 48.09945106423486, 48.57934033063693
    lon_min, lon_max = -126.33077903027713, -125.5997327646366

    df = pd.DataFrame(deployments)

    mask = (
        df["lat"].notna() & df["lon"].notna() &
        df["lat"].between(lat_min, lat_max) &
        df["lon"].between(lon_min, lon_max)
    )

    # list of devices by categories
    df = df[mask]


    # -- 3) evaluate device categories (select) -- #
    set(df['deviceCategoryCode'])

    code = "OXYSENSOR"  #obtained from deviceCategoryCode


    # number deployments by deviceCategoryCode
    err = deployments_bydeviceCategoryCode(code)


devices_list = recon_device(onc, code, lat_min, lat_max, lon_min, lon_max)

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

bla = {}
for device in devices_list[8:14]:

    date_from = device.get("begin")
    date_to   = device.get("end")

    if not date_from or not date_to or pd.isna(date_to):
        print(f"  {device['locationCode']}: skipping, no time range")
        continue

    data = onc.getDirectByLocation({
        "locationCode":       device["locationCode"],
        "deviceCategoryCode": device["deviceCategoryCode"],
        "dateFrom":           device.get("begin"),
        "dateTo":             device.get("end"),
    })

    lcode = device["locationCode"]
    bla[lcode] = {
        "lon":   device["lon"],
        "lat":   device["lat"],
        "depth": device["depth"],
        "df":    {},
    }

    for data0 in data["sensorData"]:
        prop  = data0["propertyCode"]
        t     = data0["data"]["sampleTimes"]
        v     = data0["data"]["values"]

        df_sensor = pd.DataFrame(index=t, data=v, columns=[prop])
        df_sensor.index = pd.to_datetime(df_sensor.index)
        df_sensor = df_sensor.dropna()
        df_sensor.index = df_sensor.index.tz_localize(None)

        bla[lcode]["df"][prop] = df_sensor

        # build xarray dataset with metadata
        ds = xr.Dataset(
            {prop: ("time", df_sensor[prop].values)},
            coords={"time": df_sensor.index},
            attrs={
                "locationCode": lcode,
                "deviceCategoryCode": device["deviceCategoryCode"],
                "lat":   device["lat"],
                "lon":   device["lon"],
                "depth": device["depth"],
            }
        )

        t_start = df_sensor.index[0].strftime("%Y%m%dT%H%M%S")
        t_end   = df_sensor.index[-1].strftime("%Y%m%dT%H%M%S")
        fname   = f"{lcode}_{prop}_{t_start}_{t_end}.nc"
        ds.to_netcdf(
            os.path.join(output_dir, fname),
            encoding={"time": {"units": "seconds since 1970-01-01", "dtype": "int32"}}
        )
        print(f"saved: {fname}")


