from pydantic import BaseModel
from typing import List, Union

class Record(BaseModel):
    name: str
    value: int

class TextContent(BaseModel):
    text: str

class ImageContent(BaseModel):
    url: str

class TableContent(BaseModel):
    rows: int
    columns: int
    cellData: List[List[str]]

class GraphContent(BaseModel):
    data: List[int]

class Element(BaseModel):
    id: str
    type: str
    content: Union[TextContent, ImageContent, TableContent, GraphContent]

class Report(BaseModel):
    reportName: str
    elements: List[Element]

