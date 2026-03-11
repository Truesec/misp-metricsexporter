import requests


def run(mispurl, mispkey, mispssl, diag):

    data = {}

    # Create a requests session with our authkey in the header
    sess = requests.session()
    sess.headers.update({"Authorization": mispkey, "Accept": "application/json"})

    endpoints = {
        "version": f"{mispurl}/servers/getVersion",
        "instance": f"{mispurl}/users/statistics/data",
        "attributes": f"{mispurl}/attributes/attributeStatistics",
        "orgs": f"{mispurl}/users/statistics/orgs/scope:local",
        "tags": f"{mispurl}/users/statistics/tags",
    }

    if diag:
        endpoints["diag"] = f"{mispurl}/servers/serverSettings/diagnostics"
        endpoints["feeds"] = f"{mispurl}/feeds/index"
        endpoints["servers"] = f"{mispurl}/servers/index"

    failed = []
    for key, url in endpoints.items():
        try:
            resp = sess.get(url=url, verify=mispssl)
            resp.raise_for_status()
            data[key] = resp.json()
        except Exception as e:
            failed.append(key)
            print(f"Failed to fetch {key} stats: {e}")

    data["health"] = {"healthy": len(failed) == 0, "failed": failed}

    return data
