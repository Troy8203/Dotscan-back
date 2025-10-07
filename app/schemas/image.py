from pydantic import BaseModel, constr


class ImageRequest(BaseModel):
    image_name: constr(pattern=r"^[\w\-]+\.(jpg|png|gif)$")
