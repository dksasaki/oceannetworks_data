import os
from onc import ONC
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import cartopy.feature as cfeature



def print_tree(nodes, max_levels, indent=0):
    if indent // 2 >= max_levels:
        return
    for node in nodes:
        print(" " * indent + node["locationName"])
        if "children" in node and node["children"]:
            print_tree(node["children"], max_levels, indent + 2)


def get_onc():
    token_file = os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")
    with open(token_file) as f:
        token = f.read().strip()

    onc = ONC(token=token)
    return onc



def collect_sensors(locations, onc, results=None, depth=0, max_depth=3):
    if results is None:
        results = []
    for loc in locations:
        lcode = loc["locationCode"]
        lname = loc["locationName"]
        
        try:
            cats = onc.getDeviceCategories({"locationCode": lcode})
        except Exception:
            cats = []

        for cat in cats:
            ccode = cat["deviceCategoryCode"]
            cname = cat["deviceCategoryName"]
            
            try:
                props = onc.getProperties({"locationCode": lcode, "deviceCategoryCode": ccode})
            except Exception:
                props = []

            for prop in props:
                results.append({
                    "locationCode": lcode,
                    "locationName": lname,
                    "deviceCategoryCode": ccode,
                    "deviceCategoryName": cname,
                    "propertyCode": prop["propertyCode"],
                    "propertyName": prop["propertyName"],
                })
        
        if depth < max_depth and "children" in loc and loc["children"]:
            collect_sensors(loc["children"], onc, results, depth + 1, max_depth)
    
    return results

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

def get_cdom_maps(df):
    sensor_groups = {
        'CDOM': df['deviceCategoryCode'] == 'CDOM',
    }

    styles = {
        'CDOM': dict(s=15),
    }

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={"projection": ccrs.PlateCarree()})
    ax.coastlines(resolution='10m', linewidth=1)

    for label, mask in sensor_groups.items():
        pts = df[mask][['lat', 'lon']].drop_duplicates()
        ax.scatter(pts['lon'], pts['lat'], label=label, **styles[label])

    ax.legend(loc='lower left', fontsize=8)
    plt.title("CDOM Sensors")
    plt.tight_layout()
    plt.show()

onc = get_onc()


deployments = onc.getDeployments({})

# define bounding box
lat_min, lat_max = 48.0, 55.0
lon_min, lon_max = -130.0, -120.0



df = pd.DataFrame(deployments)

get_oxygen_maps()
# mask = (
#     df["lat"].notna() & df["lon"].notna() &
#     df["lat"].between(lat_min, lat_max) &
#     df["lon"].between(lon_min, lon_max)
# )

# sensors = ['OXYSENSOR', 'CTDPHOX', 'WETLABS_WQM', 'GTD', 'CTD']



# deviceCategoryCode = set(df_filtered['deviceCategoryCode'])

#### co2 deployments?
for code in ['CO2SENSOR', 'CHEMINI', 'CORK']:
    cats = onc.getDeployments({"deviceCategoryCode": code})
    print(code, len(cats), "deployments")

    
#### oxygen
odo_mask = df['deviceCode'].str.contains('ODO', na=False)
rbr_mask = df['deviceCode'].str.contains('RBRCONCERTO', na=False)

for code in ['OXYSENSOR', 'CTDPHOX', 'GTD', 'WETLABS_WQM']:
    n = len(df[df['deviceCategoryCode'] == code])
    print(code, n, "deployments")

n_odo = len(df[odo_mask])
n_rbr = len(df[rbr_mask])
print("CTD+ODO (deviceCode)", n_odo, "deployments")
print("RBRCONCERTO (deviceCode)", n_rbr, "deployments")