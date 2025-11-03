"""
Main script to retrieve N64 game information
"""
import requests
import time
from retroachievements import RetroAchievementsAPI
from retroachievements.utils import save_to_json


def get_all_n64_games(username: str, api_key: str):
    """
    Retrieve all N64 games and their supported versions
    
    Args:
        username: Your RetroAchievements username
        api_key: Your API key
    """
    client = RetroAchievementsAPI(username, api_key)
    
    # Get all N64 games (console_id = 2)
    print("Retrieving Nintendo 64 game list...\n")
    
    try:
        all_n64_games = client.get_game_list(console_id=2, with_achievements=True)
        
        print(f"✅ {len(all_n64_games)} N64 games found\n")
        
        # Filter to exclude all games starting with ~ (hacks, homebrews, prototypes, unlicensed)
        filtered_games = [
            game for game in all_n64_games
            if not game['Title'].startswith('~') and '[Subset' not in game['Title']
        ]
        
        ignored_count = len(all_n64_games) - len(filtered_games)
        print(f"⏭️  {ignored_count} games ignored (hacks/subsets)")
        print(f"📋 {len(filtered_games)} games to process\n")
        
        # Retrieve detailed info for all games
        all_games_data = []
        
        for i, game in enumerate(filtered_games, 1):
            game_id = game['ID']
            game_title = game['Title']
            
            print(f"[{i}/{len(filtered_games)}] {game_title} (ID: {game_id})...", end='\r')
            
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    game_info = client.get_game_info(game_id)
                    time.sleep(0.5)  # Pause de 0.5s entre les requêtes
                    hashes = client.get_game_hashes(game_id)
                    
                    game_data = {
                        'game_info': game_info,
                        'supported_hashes': hashes
                    }
                    
                    all_games_data.append(game_data)
                    break
                    
                except requests.exceptions.HTTPError as e:
                    if '429' in str(e):
                        retry_count += 1
                        wait_time = 30 * retry_count  # Wait 30s, then 60s, then 90s
                        print(f"\n⚠️  Rate limit reached. Waiting {wait_time}s... ({retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print(f"\n⚠️  HTTP error for {game_title}: {e}")
                        break
                        
                except Exception as e:
                    print(f"\n⚠️  Error for {game_title}: {e}")
                    break
        
        print(f"\n\n✅ {len(all_games_data)} games retrieved successfully")
        
        # Create data directory if it doesn't exist
        from pathlib import Path
        data_dir = Path('./data')
        data_dir.mkdir(exist_ok=True)
        
        # Save all complete data
        save_to_json(all_games_data, str(data_dir / 'n64_games_data.json'))
        
        # Filter only official games (no ~, no subset)
        official_games = [
            game_data for game_data in all_games_data 
            if game_data['game_info']['ParentGameID'] is None
            and not game_data['game_info']['Title'].startswith('~')
        ]
        
        # Save only supported_hashes of official games
        all_games_data_light = [
            {
                'game_id': game_data['game_info']['ID'],
                'game_title': game_data['game_info']['Title'],
                'supported_hashes': game_data['supported_hashes']
            } 
            for game_data in official_games
        ]
        save_to_json(all_games_data_light, str(data_dir / 'n64_games_data_light.json'))
        
        print(f"📦 {len(official_games)} official game(s) in light file")
        print(f"🎉 Data retrieval complete!\n")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        print("Check your credentials (username and API key)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point"""
    import os
    import sys
    from pathlib import Path
    
    # Get credentials from environment variables or prompt user
    username = os.environ.get('RETROACHIEVEMENTS_USERNAME')
    api_key = os.environ.get('RETROACHIEVEMENTS_API_KEY')
    
    if not username:
        username = input("Enter your RetroAchievements username: ")
    
    if not api_key:
        api_key = input("Enter your RetroAchievements API key: ")
    
    if not username or not api_key:
        print("❌ Error: Username and API key are required")
        print("\nYou can set them as environment variables:")
        print("  export RETROACHIEVEMENTS_USERNAME='your_username'")
        print("  export RETROACHIEVEMENTS_API_KEY='your_api_key'")
        return
    
    # Step 1: Retrieve game data
    print("="*60)
    print("STEP 1: Retrieve N64 Game Data")
    print("="*60)
    print()
    
    success = get_all_n64_games(username, api_key)
    
    if not success:
        return
    
    # Step 2: Filter ROMs (automatic)
    roms_folder = Path("./roms")
    
    if not roms_folder.exists():
        print("\n" + "="*60)
        print("ℹ️  ROMs folder not found")
        print("="*60)
        print(f"\nTo filter ROMs, create a 'roms' folder and add your ROM files,")
        print("then run this script again.")
        return
    
    rom_files = list(roms_folder.glob("*.z64")) + list(roms_folder.glob("*.n64")) + \
                list(roms_folder.glob("*.v64")) + list(roms_folder.glob("*.zip"))
    
    if not rom_files:
        print("\n" + "="*60)
        print("ℹ️  No ROM files found in 'roms' folder")
        print("="*60)
        print(f"\nAdd your ROM files to: {roms_folder.resolve()}")
        print("then run this script again.")
        return
    
    # Filter ROMs automatically
    print("\n" + "="*60)
    print("STEP 2: Filter ROMs")
    print("="*60)
    print(f"\nFound {len(rom_files)} ROM file(s) in 'roms' folder\n")
    
    # Import and run filter_roms
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from filter_roms import filter_roms
    
    json_file = Path("./data/n64_games_data_light.json")
    if json_file.exists():
        filter_roms(str(roms_folder), str(json_file))
    else:
        print(f"❌ Error: JSON file not found: {json_file}")


if __name__ == "__main__":
    main()
