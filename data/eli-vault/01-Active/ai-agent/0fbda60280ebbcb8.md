---
id: 0fbda60280ebbcb8
source: "llm-scraper-README.md"
"title: z.string(),"
category: ai-agent
skillTags: ["code"]
containmentHash: 8eb7049185b1938b6fd0
createdAt: 1786051357033
embeddingSig: "await:browser:newpage|await:page:goto|browser:newpage:await|const:page:await|const:scraper:llmscraper|llmscraper:const:scraper|llmscraper:open:page|newpage:await:page|open:page:const|page:await:browser|page:const:page|scraper:llmscraper:open"
---
w LLMScraper
const scraper = new LLMScraper(llm)

// Open new page
const page = await browser.newPage()
await page.goto('https://news.ycombinator.com')
// Define schema to extract contents into
const schema = z.object({
  top: z
    .array(
      z.object({
        title: z.string(),
        points: z.number(),
        by: z.string(),
        commentsURL: z.string(),
      })
    )
    .length(5)