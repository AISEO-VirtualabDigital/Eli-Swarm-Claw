---
id: 65bcdf7eece86eac
source: "social-analyzer-README.md"
"title: Social Analyzer README"
category: social
skillTags: ["code"]
containmentHash: 25048cc69934a48eb496
createdAt: 1786051359303
embeddingSig: "adult:python3:username|importing:object:python|johndoe:type:adult|johndoe:websites:logs|logs:screenshots:importing|object:python:python|python3:username:johndoe|screenshots:importing:object|type:adult:python3|username:johndoe:type|username:johndoe:websites|websites:logs:screenshots"
---
n3 app.py --username "johndoe" --type "adult"
#or
python3 app.py --username "johndoe" --websites "car" --logs --screenshots
```
### Importing as object (python)
```python

#E.g. #1
from importlib import import_module
SocialAnalyzer = import_module("social-analyzer").SocialAnalyzer()
results = SocialAnalyzer.run_as_object(username="johndoe",silent=True)