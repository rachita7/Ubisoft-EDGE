from fastapi.encoders import jsonable_encoder
from typing import List, Optional, Union
# Pydantic, and Python's built-in typing are used to define a schema
# that defines the structure and types of the different objects stored
# in the recipes collection, and managed by this API.
from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic.json import ENCODERS_BY_TYPE


class PydanticObjectId(ObjectId):
    """
    Object Id field. Compatible with Pydantic.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return PydanticObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(
            type="string",
            examples=["5eb7cf5a86d9755df3a6c593", "5eb7cfb05e32e07750a1756a"],
        )


ENCODERS_BY_TYPE[PydanticObjectId] = str

class Person(BaseModel):
    _id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    linkedinURL: str
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        # if data["_id"] is None:
        #     data.pop("_id")
        return data


class Game(BaseModel):
    _id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    year: str
    platform: str
    createdBy: str
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        # if data["_id"] is None:
        #     data.pop("_id")
        return data

class WorksAt(BaseModel):
    _id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    game: str
    jobs: List[str]
    company: str
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        # if data["_id"] is None:
        #     data.pop("_id")
        return data

class VidData(BaseModel):
    _id: Optional[PydanticObjectId] = Field(None, alias="_id")
    url: str
    game: str
    company: str
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        # if data["_id"] is None:
        #     data.pop("_id")
        return data