from typing import Dict, Any
from pydantic import ConfigDict, BaseModel


class CoPilotBaseModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra='ignore',
                              protected_namespaces=('protect_me_', 'also_protect_'))

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        if "exclude_none" in kwargs:
            _ignored = kwargs.pop("exclude_none")
        return super().model_dump(*args, exclude_none=True, **kwargs)
