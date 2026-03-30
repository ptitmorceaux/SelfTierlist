from pydantic import BaseModel


class ImageUploadData(BaseModel):
    hash: str
    created: bool


class ImageUploadResponse(BaseModel):
    status: int
    data: ImageUploadData


class ImageDeleteResponse(BaseModel):
    status: int
    message: str
