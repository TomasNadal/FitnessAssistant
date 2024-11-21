from pydantic import BaseModel, Field
from typing import Optional, Union


class TextParserResponse(BaseModel):
    exercise: Union[str, None]
    series: Union[int, None]  
    repetition: Union[int, None]
    kg: Union[float, None]
    rir: Union[int, None]

