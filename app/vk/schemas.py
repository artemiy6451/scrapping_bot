from pydantic import BaseModel


class VKArticle(BaseModel):
    group_name: str
    text: str
    likes: int
    comments: int
    share: int
    link: str
