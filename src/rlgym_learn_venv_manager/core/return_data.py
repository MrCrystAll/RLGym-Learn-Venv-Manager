from pydantic import BaseModel


class PackageInfo(BaseModel):
    name: str
    version: str
    summary: str
