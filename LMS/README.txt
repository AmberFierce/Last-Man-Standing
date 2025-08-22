 Last Man Standing Tracker (Premier League Only)

## Setup
1. Create `.env` and paste your Football API and Discord bot tokens:
   ```
   API_KEY=your_football_api_key
   DISCORD_TOKEN=your_discord_bot_token
   ```
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn jinja2 python-dotenv requests discord.py
   ```
3. Run the app:
   ```bash
   uvicorn main:app --reload
   ```
4. Run the Discord bot:
   ```bash
   python discord_bot.py
   ```
5. Check results weekly:
   ```bash
   python check_results.py
   ```

## Commands
- `!pick Arsenal` → set your team
- `!leaderboard` → show who’s still in
- `!status` → see your current pick
- Admins: `!markpaid @user`, `!setpick @user Arsenal`

---
Dark mode, clean layout, Discord-integrated. GW2 ready.