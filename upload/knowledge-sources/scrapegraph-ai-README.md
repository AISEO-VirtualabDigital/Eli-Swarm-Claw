---
Source: https://github.com/ScrapeGraphAI/Scrapegraph-ai
Category: ai-agent
Description: ScrapeGraphAI — LLM-powered Python scraping framework. Uses graph-based pipelines with LangChain to extract data from websites.
FetchedAt: 2026-08-04
---
## 🚀 **Looking for an even faster and simpler way to scrape at scale (only 5 lines of code)?** Check out our enhanced version at [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&ut#m_content=top_banner)! 🚀

----------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Single-page scraper that only needs a user prompt and an input source.                                           |
| SearchGraph             | Multi-page scraper that extracts information from the top n search results of a search engine.                  |
| SpeechGraph             | Single-page scraper that extracts information from a website and generates an audio file.                       |
| ScriptCreatorGraph      | Single-page scraper that extracts information from a website and generates a Python script.                     |
| SmartScraperMultiGraph  | Multi-page scraper that extracts information from multiple pages given a single prompt and a list of sources.    |
| ScriptCreatorMultiGraph | Multi-page scraper that generates a Python script for extracting information from multiple pages and sources.     |

For each of these graphs there is the multi version. It allows to make calls of the LLM in parallel.

It is possible to use different LLM through APIs, such as **OpenAI**, **Groq**, **Azure**, **Gemini**, **[MiniMax](docs/minimax.md)** and more, or local models using **Ollama**.

Remember to have [Ollama](https://ollama.com/) installed and download the models using the **ollama pull** command, if you want to use local models.


## 📖 Documentation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

The documentation for ScrapeGraphAI can be found [here](https://docs.scrapegraphai.com/introduction).
## 🆚 Open Source vs Managed API

ScrapeGraphAI comes in two flavours: **this open-source library**, which you run yourself, and the **managed cloud API** (used via the [Python](https://github.com/ScrapeGraphAI/scrapegraph-py) and [JS/TS](https://github.com/ScrapeGraphAI/scrapegraph-js) SDKs). This table explains the difference so you can pick the right one.

| | Open Source (`scrapegraphai`) | Managed API (`scrapegraph-py` / `scrapegraph-js`) |
|---|---|---|
| **What it is** | A Python library you run yourself | A hosted cloud service you call via SDK |
| **Where it runs** | Your own infrastructure (self-hosted) | ScrapeGraphAI cloud |
| **LLM** | Bring your own (OpenAI, Groq, Gemini, Azure, local via Ollama) | Managed for you |
| **Browser / JS rendering** | You configure it (Playwright) | Managed (stealth, `auto`/`fast`/`js` modes) |
| **Proxies & anti-bot** | Your responsibility | Included |
| **Scaling & maintenance** | Your responsibility | Fully managed |
| **Cost model** | LLM tokens + your own infra | Pay-as-you-go credits |
| **Auth** | Your own LLM keys | `SGAI_API_KEY` |
| **Capabilities** | Graph pipelines (SmartScraper, Search, Speech, ScriptCreator…) | Scrape, Extract, Search, Crawl, Monitor, History |
| **Setup effort** | More configuration | Minimal — API key + one call |
| **License** | MIT | SDK is MIT; the API service is paid |

**Choose the open-source library** if you want full control, on-prem/self-hosted data, local LLMs (Ollama), or fine-grained cost tuning — and you're happy to manage browsers, proxies and scaling yourself.

**Choose the managed API** if you want zero infrastructure, managed JS rendering & anti-bot, built-in **Crawl** and scheduled **Monitor** jobs, and the fastest path to production — billed per credit.

- Open-source library: https://github.com/ScrapeGraphAI/Scrapegraph-ai
- Python SDK: https://github.com/ScrapeGraphAI/scrapegraph-py
- JS/TS SDK: https://github.com/ScrapeGraphAI/scrapegraph-js
- API docs: https://docs.scrapegraphai.com/introduction

## 🤝 Contributing

Feel free to contribute and join our Discord server to discuss with us improvements and give us suggestions!

Please see the [contributing guidelines](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 ScrapeGraph API & SDKs
If you are looking for a quick solution to integrate ScrapeGraph in your system, check out our powerful API [here!](https://scrapegraphai.com)

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://scrapegraphai.com)

We offer SDKs in both Python and Node.js, making it easy to integrate into your projects. Check them out below:

| SDK       | Language | GitHub Link                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://docs.scrapegraphai.com/sdks/python) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://docs.scrapegraphai.com/sdks/javascript) |

The Official API Documentation can be found [here](https://docs.scrapegraphai.com/introduction).

## 📈 Telemetry
We collect anonymous usage metrics to enhance our package's quality and user experience. The data helps us prioritize improvements and ensure compatibility. If you wish to opt-out, set the environment variable SCRAPEGRAPHAI_TELEMETRY_ENABLED=false. For more information, please refer to the documentation [here](https://docs.scrapegraphai.com/introduction).

## ❤️ Contributors
[![Contributors](https://contrib.rocks/image?repo=ScrapeGraphAI/Scrapegraph-ai)](https://github.com/ScrapeGraphAI/Scrapegraph-ai/graphs/contributors)

## 🎓 Citations
If you have used our library for research purposes please quote us with the following reference:
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/ScrapeGraphAI/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```
## Authors

|                    | Contact Info         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 License

ScrapeGraphAI is licensed under the MIT License. See the [LICENSE](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/LICENSE) file for more information.

## Acknowledgements

- We would like to thank all the contributors to the project and the open-source community for their support.
- ScrapeGraphAI is meant to be used for data exploration and research purposes only. We are not responsible for any misuse of the library.

Made with ❤️ by [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
