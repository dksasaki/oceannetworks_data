# oceannetworks_data

Python environment for downloading and exploring data from [Ocean Networks Canada (ONC)](https://www.oceannetworks.ca/) via the [Oceans 3.0 API](https://data.oceannetworks.ca/OpenAPI).

---

## Requirements

- [pixi](https://pixi.sh) — cross-platform package manager

---

## Installation

### 1. Install pixi

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### 2. Clone the repository

```bash
git clone https://github.com/dksasaki/oceannetworks_data.git
cd oceannetworks_data
```

### 3. Install the environment

```bash
pixi install
```

This will install all dependencies defined in `pixi.toml`.

---

## ONC API Token

An API token is required to access ONC data.

### Obtaining a token

1. Register at https://data.oceannetworks.ca/Registration
2. Log in at https://data.oceannetworks.ca
3. Click **Profile** (top right corner)
4. Go to the **Web Services API** tab
5. Click **Copy Token**

### Storing the token

Create a `.login` file at the root of the project and paste your token:

```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

The token is read automatically by the scripts:

```python
import os
with open(os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")) as f:
    token = f.read().strip()
```

> **Important:** Add `.login` to your `.gitignore` to avoid accidentally sharing your token.

```bash
echo ".login" >> .gitignore
```

---

## Usage

Launch an interactive IPython session:

```bash
pixi run ipython
```

Basic example:

```python
import os
from onc import ONC

with open(os.path.join(os.environ["PIXI_PROJECT_ROOT"], ".login")) as f:
    token = f.read().strip()

onc = ONC(token)



# get all deployments
deployments = onc.getDeployments({})
```

---

## References

- ONC Data Portal: https://data.oceannetworks.ca
- ONC API documentation: https://oceannetworkscanada.github.io/Oceans3.0-API
- Python client library: https://oceannetworkscanada.github.io/api-python-client