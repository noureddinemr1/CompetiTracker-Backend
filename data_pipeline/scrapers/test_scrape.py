from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List

app = FirecrawlApp(api_key='fc-b75c7ffc064941369610bec7c2227513')



class ExtractSchema(BaseModel):
    url: str
    name : str
    description: str

data = app.extract([
  "https://spacenet.tn/74-pc-portable-tunisie"
], {
    'prompt': 'enter each product and get all the fields i want',
    'schema': ExtractSchema.model_json_schema(),
})
print(data)