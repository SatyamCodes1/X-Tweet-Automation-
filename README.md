# X Funny News Bot (Free-Tier Friendly)

Automates posting funny, Gen‑Z flavored news and X trends to your X account.  
Includes:
- X Trends (3×/day)
- GNews + NewsAPI combo with caching
- SQLite de‑dupe
- Meme image generation (PIL)
- Free LLM (Groq Llama 3) support
- GitHub Actions schedule (free)
- `TEST_MODE` so you can test locally without posting

## Quickstart (Local Test)
```bash
pip install -r requirements.txt
cp .env.example .env  # fill keys
TEST_MODE=true python -m src.run TRIGGER=trend_window   # simulate trend post
TEST_MODE=true python -m src.run TRIGGER=cache_news     # cache news
TEST_MODE=true python -m src.run TRIGGER=news_batch     # simulate news post
```
Meme images are saved in `out/`. SQLite DB: `bot.sqlite3`.

## Deploy (Live on GitHub Actions)
1. Push repo to GitHub.
2. Add **Repo → Settings → Secrets and variables → Actions**:
   - `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`
   - `GROQ_API_KEY`, `GNEWS_API_KEY`, `NEWSAPI_KEY`
3. Add **Variables**: `WOEID=23424848`, `DEFAULT_COUNTRY=in`
4. Ensure live mode by setting `TEST_MODE=false` in workflow env or removing it from `.env` on CI.
5. Actions will run on schedule and post.

## Notes
- Stays under X Free 500 posts/mo if you keep ~12/day.
- We call X trends 3×/day to conserve reads.
- Change meme template in `.env` via `MEME_TEMPLATE`.
