import urllib3, os, configparser, logging
from modules import convert_data, fetch_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cwd = os.getcwd()
config_path = f"{cwd}/config.ini"
dev_config_path = f"{cwd}/devconfig.ini"

if os.path.isfile(dev_config_path):
    logger.info(f"Using development config at {dev_config_path}")
    config_path = dev_config_path

if not os.path.isfile(config_path):
    raise Exception(
        f"Config file not found or accessible, make sure config.ini exists at {config_path}"
    )

try:
    config = configparser.ConfigParser()
    config.read(config_path)

    misp_url = config["connection"]["misp_url"]
    misp_key = config["connection"]["misp_key"]
    misp_ssl = eval(config["connection"]["misp_ssl"])

    instancename = config["preferences"]["instance_name"]
    diagnostics = eval(config["preferences"]["include_diagnostics"])
except:
    raise Exception("Failure reading config file, make sure it is configured correctly")

if not misp_ssl:
    # Disable warnings to stdout if not validating SSL
    urllib3.disable_warnings()

if __name__ == "__main__":
    data = fetch_data.run(
        mispurl=misp_url, mispkey=misp_key, mispssl=misp_ssl, diag=diagnostics
    )
    metrics = convert_data.run(data=data, instancename=instancename)
    print(metrics, end="")
