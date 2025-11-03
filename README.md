# RetroAchievements - N64 Games Info

Retrieves information about supported game versions for Nintendo 64 games from RetroAchievements.org.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Method 1: Environment Variables (Recommended)

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
RETROACHIEVEMENTS_USERNAME=your_username
RETROACHIEVEMENTS_API_KEY=your_api_key
```

Get your API key from: https://retroachievements.org/controlpanel.php

Then load it before running:

```bash
# For bash/zsh
set -a && source .env && set +a
python main.py

# Or in one line
source .env && python main.py
```

### Method 2: Interactive Prompt

Simply run the script and it will prompt you for credentials:

```bash
python main.py
```

## Usage

### Option 1: All-in-one (Recommended)

Run the main script which will retrieve game data and optionally filter ROMs in one go:

```bash
python main.py
```

The script will:

1. Retrieve all N64 games data from RetroAchievements
2. Generate JSON files in `data/` folder
3. Detect if you have a `roms/` folder with ROM files
4. Ask if you want to filter ROMs immediately

### Option 2: Step-by-step

#### Step 1: Get N64 games data

```bash
python main.py
```

This retrieves all official N64 games with achievements and their supported ROM hashes.

**Output:**

- `data/n64_games_data.json`: Complete game data with achievements
- `data/n64_games_data_light.json`: Only game IDs, titles, and supported hashes

#### Step 2: Filter ROMs (optional, standalone)

```bash
# Default paths (./roms and ./data/n64_games_data_light.json)
python filter_roms.py

# Or with custom paths
python filter_roms.py /path/to/roms /path/to/json
```

This script:

- Scans your ROM files (supports `.z64`, `.n64`, `.v64`, `.zip`)
- Matches them against supported hashes from the JSON
- Applies region priority: France > Europe > USA
- Copies and unzips supported ROMs to `roms/filtered/` subfolder

## Project Structure

```
RetroHash/
├── retroachievements/
│   ├── __init__.py            # Main package
│   ├── client.py              # API client
│   ├── display.py             # Display functions
│   └── utils.py               # Utilities
├── data/                      # Generated data (auto-created)
│   ├── n64_games_data.json    # Complete game data
│   └── n64_games_data_light.json  # Light version (hashes only)
├── roms/                      # Your ROM files (create manually)
│   └── filtered/              # Filtered ROMs (auto-created)
├── main.py                    # Main script (data + filtering)
├── filter_roms.py             # Standalone ROM filtering script
├── .env.example               # Example environment file
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## Features

- ✅ Retrieve all N64 games with achievements from RetroAchievements API
- ✅ Filter out hacks, homebrews, prototypes, and subsets
- ✅ Generate two JSON files (full and light versions) in `data/` folder
- ✅ Filter ROMs by supported hashes with region priority (France > Europe > USA)
- ✅ Automatically unzip supported ROMs to `roms/filtered/`
- ✅ Rate limiting handling with automatic retries
- ✅ All-in-one workflow: data retrieval + ROM filtering in one command
- ✅ Portable: works on any machine without hardcoded paths

## Notes

- The script respects API rate limits with 0.5s delays between requests
- If rate limited (429 errors), it will automatically retry with exponential backoff (30s, 60s, 90s)
- Only official games are included in the light JSON (no hacks, subsets, etc.)
- ROM filtering uses MD5 hashes to ensure correct versions
- JSON files are saved in `data/` folder for better organization
- Create a `roms/` folder and add your ROM files before filtering
