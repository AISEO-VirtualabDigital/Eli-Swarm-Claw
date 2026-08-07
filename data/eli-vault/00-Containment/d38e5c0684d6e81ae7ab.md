---
id: 620fe08ba0a1eabb
source: "claude-repurpose-README.md"
"title: Claude Repurpose"
category: ai-agent
skillTags: ["code"]
containmentHash: d38e5c0684d6e81ae7ab
createdAt: 1786051353100
embeddingSig: "calendar:from:outputs|calendar:works:input|content:content:extraction|content:extraction:youtube|extraction:youtube:transcript|from:outputs:repurpose|input:content:content|lishing:calendar:from|outputs:repurpose:calendar|repurpose:calendar:works|works:input:content|youtube:transcript:auto"
---
lishing calendar from outputs
/repurpose calendar
```
## How It Works

```
Input (any content)
      |
      v
  Content Extraction        YouTube -> transcript
  (auto-detect type)        Blog URL -> article text
                            Audio -> Whisper transcription
                            Local file -> direct read
      |
      v
  Content Atomization       Extract 5-15 reusable atoms: