from prometheus_client import CollectorRegistry, Gauge, generate_latest


# Instance wide stats
def instancestats(instance, attributes, instancename, registry):
    g = Gauge(
        "instance_events_total",
        "Total number of events on the MISP instance",
        labelnames=["instancename"],
        namespace="misp",
        registry=registry,
    )
    g.labels(instancename=instancename).set(instance["stats"]["event_count"])
    g = Gauge(
        "instance_attributes_total",
        "Total number of attributes on the MISP instance",
        labelnames=["instancename"],
        namespace="misp",
        registry=registry,
    )
    g.labels(instancename=instancename).set(instance["stats"]["attribute_count"])
    g = Gauge(
        "instance_correlations_total",
        "Total number of correlations on the MISP instance",
        labelnames=["instancename"],
        namespace="misp",
        registry=registry,
    )
    g.labels(instancename=instancename).set(instance["stats"]["correlation_count"])

    g = Gauge(
        "instance_attributes_per_type",
        "Total number of attributes per type on the MISP instance",
        labelnames=["type", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for type in attributes:
        g.labels(type=type, instancename=instancename).set(attributes[type])


# Organisation stats
def orgstats(data, instancename, registry):
    g = Gauge(
        "org_events_total",
        "Total number of events per org on the MISP instance",
        labelnames=["orgid", "orgname", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for org in data:
        try:
            data[org]["eventCount"]
        except:
            continue
        g.labels(
            orgid=data[org]["id"], orgname=data[org]["name"], instancename=instancename
        ).set(data[org]["eventCount"])
    g = Gauge(
        "org_attributes_total",
        "Total number of attributes per org on the MISP instance",
        labelnames=["orgid", "orgname", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for org in data:
        try:
            data[org]["attributeCount"]
        except:
            continue
        g.labels(
            orgid=data[org]["id"], orgname=data[org]["name"], instancename=instancename
        ).set(data[org]["attributeCount"])


# Diagnostic data
def diagnostics(data, instancename, registry):
    # Update status
    g = Gauge(
        "up_to_date",
        "MISP update status",
        labelnames=["instancename"],
        namespace="misp",
        registry=registry,
    )
    if data["version"]["upToDate"] == "same":
        g.labels(instancename=instancename).set(1)
    else:
        g.labels(instancename=instancename).set(0)
    # Worker status
    g = Gauge(
        "workers_healthy",
        "Checks if workers are healthy",
        labelnames=["workertype", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for worker_type in ["cache", "default", "email", "prio", "update", "scheduler"]:
        if data["workers"][worker_type]["ok"]:
            g.labels(workertype=worker_type, instancename=instancename).set(1)
        else:
            g.labels(workertype=worker_type, instancename=instancename).set(0)


# Tag stats
def tags(data, instancename, registry):
    g = Gauge(
        "tlp_stats",
        "Count of TLP tags on instance",
        labelnames=["tlp", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for tlp in [
        "tlp:red",
        "tlp:amber+strict",
        "tlp:amber",
        "tlp:green",
        "tlp:white",
        "tlp:clear",
    ]:
        if tlp in data["flatData"]["tlp"]:
            metric = tlp.translate(str.maketrans({":": "_", "+": "_"}))
            g.labels(tlp=metric, instancename=instancename).set(
                data["flatData"]["tlp"][tlp]["size"]
            )


# Health status
def health(data, version, instancename, registry):
    g = Gauge(
        "healthy",
        "Whether the MISP instance is healthy (1 = healthy, 0 = unhealthy)",
        labelnames=["instancename"],
        namespace="misp",
        registry=registry,
    )
    g.labels(instancename=instancename).set(1 if data["healthy"] else 0)

    g = Gauge(
        "endpoint_reachable",
        "Whether a specific MISP endpoint is reachable (1 = reachable, 0 = unreachable)",
        labelnames=["endpoint", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for endpoint in [
        "version",
        "instance",
        "attributes",
        "orgs",
        "tags",
        "diag",
        "feeds",
        "servers",
    ]:
        reachable = 0 if endpoint in data["failed"] else 1
        g.labels(endpoint=endpoint, instancename=instancename).set(reachable)

    if version:
        g = Gauge(
            "version_info",
            "MISP version info",
            labelnames=[
                "version",
                "perm_sync",
                "perm_sighting",
                "perm_galaxy_editor",
                "instancename",
            ],
            namespace="misp",
            registry=registry,
        )
        g.labels(
            version=version.get("version", "unknown"),
            perm_sync=version.get("perm_sync", "unknown"),
            perm_sighting=version.get("perm_sighting", "unknown"),
            perm_galaxy_editor=version.get("perm_galaxy_editor", "unknown"),
            instancename=instancename,
        ).set(1)


# Feed stats
def feedstats(data, instancename, registry):
    g_events = Gauge(
        "feed_event_count",
        "Number of events pulled from a feed",
        labelnames=["feed_id", "feed_name", "feed_provider", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for feed in data:
        f = feed.get("Feed", feed)
        if not f.get("enabled"):
            continue
        labels = {
            "feed_id": f.get("id", "unknown"),
            "feed_name": f.get("name", "unknown"),
            "feed_provider": f.get("provider", "unknown"),
            "instancename": instancename,
        }
        g_events.labels(**labels).set(f.get("event_count", 0) or 0)


# Sync server stats
def serverstats(data, instancename, registry):
    g_last_pull = Gauge(
        "server_last_pull_timestamp",
        "Timestamp of the last successful pull from a sync server",
        labelnames=["server_id", "server_name", "server_url", "instancename"],
        namespace="misp",
        registry=registry,
    )
    g_last_push = Gauge(
        "server_last_push_timestamp",
        "Timestamp of the last successful push to a sync server",
        labelnames=["server_id", "server_name", "server_url", "instancename"],
        namespace="misp",
        registry=registry,
    )
    for server in data:
        s = server.get("Server", server)
        labels = {
            "server_id": s.get("id", "unknown"),
            "server_name": s.get("name", "unknown"),
            "server_url": s.get("url", "unknown"),
            "instancename": instancename,
        }
        g_last_pull.labels(**labels).set(s.get("lastpulledid", 0) or 0)
        g_last_push.labels(**labels).set(s.get("lastpushedid", 0) or 0)


def run(data, instancename):
    # Create a Prometheus registry
    registry = CollectorRegistry()

    # Health metric is always exported
    health(data["health"], data.get("version"), instancename, registry)

    # Prepare data and add to registry
    if "instance" in data and "attributes" in data:
        instancestats(data["instance"], data["attributes"], instancename, registry)
    if "orgs" in data:
        orgstats(data["orgs"], instancename, registry)
    if "tags" in data:
        tags(data["tags"], instancename, registry)

    # Only convert diagnostics if it exists
    if "diag" in data:
        diagnostics(data["diag"], instancename, registry)
    if "feeds" in data:
        feedstats(data["feeds"], instancename, registry)
    if "servers" in data:
        serverstats(data["servers"], instancename, registry)

    # Convert the registry to a printable format and return
    metrics = generate_latest(registry).decode()
    return metrics
