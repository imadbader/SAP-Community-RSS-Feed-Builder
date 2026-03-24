# 📡 SAP Community RSS Feed Builder

A zero-dependency, single-file web tool for **SAP Digital Solution Advisors, BTP practitioners, and SAP Community members** to instantly generate, save, and share web and RSS feed URLs for [community.sap.com](https://community.sap.com).

Deployable as a static GitHub Pages site — no server, no build step, no login required.

---

## Why This Tool Exists

[community.sap.com](https://community.sap.com) is one of the richest technical resources in the SAP ecosystem — covering BTP, S/4HANA, Integration Suite, AI, ABAP, and hundreds of other topics through blog posts, Q&A threads, and discussions authored by SAP engineers, partners, and community members worldwide.

The challenge is keeping up with it.

SAP Community allows you to subscribe to areas and follow tags through its notification system, but this creates a flood of emails and in-platform alerts — not ideal for practitioners who prefer a single, curated reading environment like an RSS reader (Feedly, Inoreader, NetNewsWire, etc.).

RSS feeds solve this by letting you pull content on your own schedule, aggregate multiple sources in one place, and filter by topic without platform noise. This tool makes building those feed URLs fast and accurate — particularly useful for SAP advisors who want to stay current across multiple product areas simultaneously without manually constructing URLs or hunting through community documentation.

---

## What the Tool Does

### Feed Builder

Two feed types are supported — **Tag** and **Board / Blog Area**.

**Tag** — type any SAP managed tag name, or click a tag in the browser below the form. The tool generates three URLs:
- The tag's web page on community.sap.com
- SAP's native keyword-search RSS feed (flagged as imprecise — see limitations below)
- Two accurate RSS feeds via the rss-scn third-party API — one for blog posts, one for Q&A

**Board / Blog Area** — select from a pre-populated dropdown of verified SAP Community boards, grouped by product area. The tool generates the correct board web page URL and board-level RSS feed. Board IDs are complex Khoros-specific compound strings that cannot be reliably derived from a name, which is why this feed type uses a curated dropdown rather than a free-text field.

All URLs are rendered with one-click copy and open-in-browser buttons.

### Tag Browser

A searchable, categorized browser of SAP managed tags across 16 product and topic categories — BTP Platform, Integration Suite, SAP Build, AI & Joule, Data & Analytics, Application Development, S/4HANA, HCM, CX, Finance, Supply Chain, Security, DevOps & ALM, Basis, Sustainability, and Learning & Community. Click any tag to prefill the feed builder instantly. Category filter pills and a live search box narrow the list as you type.

All tag names are taken **verbatim from the official SAP managed tag registry** provided by SAP Community. This ensures rss-scn API requests use exact matching tag titles and avoid "SAP Managed Tag title not found" errors. Notable exact-match requirements from the official list include names like `Cloud Integration` (not `SAP Cloud Integration`), `API Management` (not `SAP API Management`), `BW (SAP Business Warehouse)` (not `SAP Business Warehouse`), and `SAP BTP, ABAP environment` (with comma, not without).

### Save, Export & Import

Save feeds to a persistent local list (browser `localStorage`). Export your collection in four formats — JSON, CSV, OPML (for direct import into RSS readers), or Markdown. Share a JSON export with teammates who can paste it into the Import field to load your entire feed list in seconds.

### URL Reference Tab

Documents all known SAP Community URL and RSS patterns, the platform limitations described below, and the third-party rss-scn API format.

---

## Getting Started

### Open Directly in a Browser
Download `index.html` and open it locally. No installation required.

### Deploy to GitHub Pages
1. Fork or clone this repo
2. Go to **Settings → Pages**
3. Set source to `main` branch, root `/`
4. Your tool will be live at `https://<your-org>.github.io/<repo-name>/`

### Open in VS Code with Claude Code
```bash
git clone https://github.com/<your-org>/sap-rss-generator.git
code sap-rss-generator
```
Open `index.html` with the Live Server extension, or refine and redeploy using Claude Code directly in VS Code.

---

## ⚠️ SAP Community RSS Limitations

Understanding the current state of RSS on the SAP Community platform is important context for using this tool correctly.

### Platform Migration Background

SAP Community migrated from its previous platform to a new environment powered by [Khoros](https://khoros.com/) in 2024. While Khoros provides some built-in RSS capabilities, the migration introduced significant regressions compared to the old SCN (SAP Community Network) platform — particularly around per-tag RSS feeds.

### The Managed Tag RSS Problem

The SAP Community platform exposes a search-based RSS endpoint:

```
https://community.sap.com/khhcw49343/rss/search?q=tags:[Tag Name]
```

Through practical testing, this endpoint has a significant flaw: **it performs a loose keyword search rather than a strict managed tag filter**.

In practice this means:
- A feed for `SAP AI Core` returns posts tagged only `Artificial Intelligence` because the words appear in the tag name
- Posts correctly tagged with `SAP AI Core` may not appear if the search scoring deprioritises them
- The same inaccuracy affects every managed tag, not just `SAP AI Core`

This is not a bug in URL construction — it is a fundamental limitation of the `/rss/search` endpoint on the Khoros platform. SAP has acknowledged community feedback around this, and the issue remains unresolved as of the time of writing.

### The Board ID Problem

Khoros board IDs are compound strings (e.g. `application-developmentblog-board`, `integrationblog-board`) that are not derivable from a product or board name. Using an incorrect board ID returns a "Node was not found" error on community.sap.com. The tool's board dropdown contains only IDs verified from real community.sap.com URLs — any board that could not be confirmed has been excluded.

### What Does and Doesn't Work Natively

| Feed Type | Native SAP RSS | Accuracy |
|---|---|---|
| All community content | `/khhcw49343/rss/Community` | ✅ Works well |
| All blog posts | `…?interaction.style=blog` | ✅ Works well |
| All Q&A | `…?interaction.style=qanda` | ✅ Works well |
| All discussions | `…?interaction.style=forum` | ✅ Works well |
| Specific board | `/rss/board?board.id=[board-id]` | ✅ Works well (with correct ID) |
| Specific managed tag | `/rss/search?q=tags:[name]` | ⚠️ Keyword match only — imprecise |
| Tag filtered to blogs only | Not natively available | ❌ Not supported |

---

## Third-Party Solution: rss-scn by Marian Füssel

Because the SAP Community platform does not provide accurate managed-tag RSS feeds natively, this tool generates URLs for a community-built alternative: **[rss-scn](https://github.com/marianfoo/rss-scn)** by [Marian Füssel](https://github.com/marianfoo).

### What rss-scn Does

rss-scn is an open-source Node.js server that acts as a bridge between your RSS reader and the SAP Community API. Instead of using the flawed `/rss/search` keyword endpoint, it queries the SAP Community platform's underlying Khoros API directly using the `managedTag.title` filter — which performs an exact match against the platform's managed tag taxonomy.

The public hosted instance is available at `https://rss-scn.marianzeis.de`.

### API Format

```
https://rss-scn.marianzeis.de/api/messages?conversation.style=[blog|qanda]&managedTag.title=[Tag%20Name]&feeds.replies=false
```

**Important:** `conversation.style` is a **required parameter** when filtering by `managedTag.title`. The API returns an error if omitted. Blog posts and Q&A must be requested as separate feeds.

**Important:** `managedTag.title` must **exactly match** the tag title as registered in the SAP Community managed tag registry. The tool's tag browser contains only verified managed tag names — using a tag name that isn't registered will return a "SAP Managed Tag title not found" error. Generic concepts (`Clean Core`), abbreviations (`SAP HCM`), and program names (`RISE with SAP`) are not registered managed tags and have been excluded from the browser.

**Examples for SAP AI Core:**
```
# Blog posts
https://rss-scn.marianzeis.de/api/messages?conversation.style=blog&managedTag.title=SAP%20AI%20Core&feeds.replies=false

# Q&A
https://rss-scn.marianzeis.de/api/messages?conversation.style=qanda&managedTag.title=SAP%20AI%20Core&feeds.replies=false
```

### Available Parameters

| Parameter | Required | Values | Description |
|---|---|---|---|
| `conversation.style` | Yes (with managedTag) | `blog`, `qanda` | Content type |
| `managedTag.title` | No | Tag display name (URL-encoded) | Exact managed tag filter |
| `managedTag.id` | No | Tag ID | Alternative to title |
| `author.id` | No | Community username | Filter by author |
| `board.id` | No | Board ID | Filter by board |
| `subject` | No | Text | Partial subject match |
| `feeds.replies` | No | `true`, `false` | Include reply content |

### Hosting Your Own Instance

```bash
git clone https://github.com/marianfoo/rss-scn.git
cd rss-scn
npm install
node index.js
# Server starts on port 3100 by default
```

---

## Acknowledgements

This tool was built on the research and open-source work of two SAP community contributors whose work is the foundation for understanding how RSS functions on the current SAP Community platform.

### Antonio Maradiaga — RSS Feed Research

[Antonio Maradiaga](https://community.sap.com/t5/user/viewprofilepage/user-id/107) ([@ajmaradiaga](https://github.com/ajmaradiaga)) conducted the foundational research into how the Khoros-based SAP Community platform structures its RSS feeds. His published findings documented the community ID (`khhcw49343`), the `/rss/Community`, `/rss/search`, and `/rss/board` endpoint patterns, verified board IDs, the `interaction.style` content type parameter, and the limitations of the managed tag search endpoint. His research is the primary source for the URL patterns and verified board IDs used in this tool.

- **Blog post:** [Exploring the RSS feeds of the new SAP Community platform](https://community.sap.com/t5/what-s-new/exploring-the-rss-feeds-of-the-new-sap-community-platform/ba-p/13594677)
- **Blog post:** [Additional SAP Community feeds](https://ajmaradiaga.com/additional-SAP-Community-feeds/)
- **Personal site:** [ajmaradiaga.com](https://ajmaradiaga.com)
- **GitHub:** [github.com/ajmaradiaga](https://github.com/ajmaradiaga)

### Marian Füssel — rss-scn Open Source Project

[Marian Füssel](https://github.com/marianfoo) built [rss-scn](https://github.com/marianfoo/rss-scn), the open-source RSS server that solves the managed tag accuracy problem by querying the SAP Community API directly with `managedTag.title` filtering. His work was directly inspired by Antonio's research and fills a critical gap in the platform's native capabilities.

- **SAP Community blog post:** [Personalized SAP Community RSS Feeds: Open Source Tool for Following Managed Tags](https://community.sap.com/t5/technology-blog-posts-by-members/personalized-sap-community-rss-feeds-open-source-tool-for-following-managed/ba-p/13950836)
- **GitHub repo:** [github.com/marianfoo/rss-scn](https://github.com/marianfoo/rss-scn)
- **Live API:** [rss-scn.marianzeis.de](https://rss-scn.marianzeis.de)

---

## URL Pattern Reference

### General Community Feeds (SAP Native)

| Content | URL |
|---|---|
| Everything | `https://community.sap.com/khhcw49343/rss/Community` |
| Blog posts | `…/rss/Community?interaction.style=blog` |
| Q&A | `…/rss/Community?interaction.style=qanda` |
| Discussions | `…/rss/Community?interaction.style=forum` |
| Events | `…/rss/Community?interaction.style=occasion` |
| Knowledge base | `…/rss/Community?interaction.style=tkb` |

Add `&count=N` to control item count, and `&feeds.replies=true` to include replies.

### Tag Feeds

| Type | URL |
|---|---|
| Tag web page | `https://community.sap.com/t5/tag/[Tag%20Name]/tg-p` |
| Tag RSS — SAP native (imprecise) | `https://community.sap.com/khhcw49343/rss/search?q=tags:[Tag%20Name]` |
| Tag blogs — accurate (rss-scn) | `https://rss-scn.marianzeis.de/api/messages?conversation.style=blog&managedTag.title=[Tag%20Name]&feeds.replies=false` |
| Tag Q&A — accurate (rss-scn) | `https://rss-scn.marianzeis.de/api/messages?conversation.style=qanda&managedTag.title=[Tag%20Name]&feeds.replies=false` |

Tag names must be percent-encoded in all URLs (spaces → `%20`). The tool handles this automatically.

### Board / Blog Area Feeds

Board IDs are Khoros-specific compound strings verified from real community.sap.com URLs. The board page suffix varies by content type: `bg-p` for blog posts, `bd-p` for discussions, `qa-p` for Q&A, `eb-p` for events.

| Type | URL |
|---|---|
| Board web page | `https://community.sap.com/t5/[url-slug]/[page-suffix]/[board-id]` |
| Board RSS | `https://community.sap.com/khhcw49343/rss/board?board.id=[board-id]` |

### Verified Board IDs

| Board | URL Slug | Board ID | Page Suffix |
|---|---|---|---|
| Technology Blog Posts by SAP | `technology-blog-posts-by-sap` | `technology-blog-postsbysa-board` | `bg-p` |
| Technology Blog Posts by Members | `technology-blog-posts-by-members` | `technology-blog-members` | `bg-p` |
| Integration — Blog Posts | `integration-blog-posts` | `integrationblog-board` | `bg-p` |
| Application Development — Blog Posts | `application-development-blog-posts` | `application-developmentblog-board` | `bg-p` |
| ABAP Cloud — Blog Posts | `abap-cloud-blog-posts` | `abap-cloudblog-board` | `bg-p` |
| ABAP Cloud — Forum | `abap-cloud-forum` | `abap-cloudforum-board` | `bd-p` |
| Enterprise Architecture — Blog Posts | `enterprise-architecture-blog-posts` | `Enterprise-Architectureblog-board` | `bg-p` |
| Enterprise Architecture — Discussions | `enterprise-architecture-discussions` | `Enterprise-Architectureforum-board` | `bd-p` |
| Data & Analytics — Blog Posts | `data-and-analytics-blog-posts` | `data-analyticsblog-board` | `bg-p` |
| ERP — Q&A | `enterprise-resource-planning-q-a` | `erp-questions` | `qa-p` |
| Technology — Q&A | `technology-q-a` | `technology-questions` | `qa-p` |
| SAP CodeJam — Blog Posts | `sap-codejam-blog-posts` | `code-jamblog-board` | `bg-p` |
| What's New | `what-s-new` | `whatsnewblog-board` | `bg-p` |

### Community ID

All SAP Community RSS feed paths include the community ID `khhcw49343`. This is the Khoros identifier for `community.sap.com` and is required in every `/rss/` path.

---

## Customisation

The entire tool is a single `index.html` file. Everything can be edited directly in VS Code or Claude Code.

| What to change | Where in the file |
|---|---|
| Tag list and categories | `SAP_TAGS` array in `<script>` |
| Board dropdown options | `<select id="boardSelect">` in HTML |
| URL construction logic | `buildURLs()` function |
| Community ID | `COMMUNITY_ID` constant |
| rss-scn base URL | `buildURLs()` — accurate tag section |

---

## Export Formats

| Format | Best for |
|---|---|
| **JSON** | Sharing with teammates, re-importing into the tool |
| **CSV** | Tracking feeds in Excel or Google Sheets |
| **OPML** | Direct import into Feedly, Inoreader, NetNewsWire, NewsBlur |
| **Markdown** | Documenting feeds in Confluence, Notion, or a GitHub wiki |

---

## License

MIT — free to use, adapt, and distribute for internal team tooling or personal use.
