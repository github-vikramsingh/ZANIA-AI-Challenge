import os
import string
import sys
from collections import defaultdict

import yaml
from fastapi.logger import logger
from src.startup_constants import APP_NAME

config = {}


class ConfigClient:
    """
        Read from local yaml file, replace all the environment variables with actual values
    """

    config_path = ""

    def __init__(self,
                 app_name,
                 profile=os.getenv("ENVIRONMENT_NAME"),
                 **kwargs
                 ):
        self.profile = profile
        self.app_name = app_name
        self.kwargs = kwargs
        logger.debug("Configuration Client Object Created.")

    @property
    def url(self) -> str:
        return self._url.format(address=self.address, app_name=self.app_name, label=self.label, filename=self.filename)

    @url.setter
    def url(self, pattern: str) -> None:
        if not pattern:
            raise ValueError("Invalid URL")
        self._url = pattern

    @property
    def filename(self) -> str:
        if self._filename.find(".") == -1:
            return f"{self._filename}.yaml"
        return self._filename

    @filename.setter
    def filename(self, path):
        if not path:
            raise ValueError("Invalid filename")
        if path.find(".") == -1:
            path = f"{path}.yaml"
        self._filename = path

    def __load_yaml(self, f, context):

        def string_constructor(loader, node):
            t = string.Template(node.value)
            value = t.substitute(context)
            return value

        l = yaml.SafeLoader
        l.add_constructor('tag:yaml.org,2002:str', string_constructor)

        token_re = string.Template.pattern
        l.add_implicit_resolver('tag:yaml.org,2002:str', token_re, None)

        x = yaml.load(f, Loader=l)
        return x

    def __read_config__(self) -> dict:
        if not os.path.exists(self.config_path):
            raise EnvironmentError(f"Unable to find Configuration file: {self.config_path}")
        with open(self.config_path) as f:
            if self.config_path.endswith(("yaml", "yml")):
                try:
                    return self.__load_yaml(f, os.environ)
                except Exception as e:
                    logger.error(e)
                    logger.error("Error in loading yaml ", exc_info=True)

    def get_config(self) -> dict:
        file_name = self.app_name + '.yml'
        self.config_path = os.path.abspath(os.path.join(self.kwargs.get("custom_path") or "", file_name))
        logger.info(f"Reading Configuration from local file {self.config_path}")
        return self.__read_config__()


# if exception retry 3 times with 10 second wait
def get_configurations(app_name=os.getenv("APP_NAME", APP_NAME),
                       custom_path=os.getenv("CUSTOM_CONFIGURATION_PATH", "src")):
    """
    Args:
        app_name (): Spring Cloud config label
        custom_path (): Custom path of local file

    Returns: Configuration dictionary
    """
    client = ConfigClient(
        app_name=app_name,
        custom_path=custom_path
    )
    config_data = client.get_config()
    config_loaded = defaultdict(str)
    if config_data:
        other_env_keys = filter(lambda env: env != "ENVIRONMENT_VARIABLES", config_data)
        for each in other_env_keys:
            config_loaded[each] = os.environ.get(each, config_data[each])
    return config_loaded


def get_config():
    global config
    if config:
        return config
    config = get_configurations()
    return config


try:
    config = get_configurations()
except Exception as e:
    logger.error("#### Error getting configuration after retries", exc_info=True)
    sys.exit(1)
