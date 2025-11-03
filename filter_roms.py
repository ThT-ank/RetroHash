"""
Script to filter ROMs based on supported hashes
"""
import json
import hashlib
import shutil
import zipfile
from pathlib import Path


def calculate_md5(file_path):
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest().upper()


def calculate_md5_from_zip(zip_path):
    """Calculate MD5 hash of the ROM file inside a ZIP"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the ROM file in the ZIP
            rom_files = [f for f in zip_ref.namelist() if f.endswith(('.z64', '.n64', '.v64'))]
            if not rom_files:
                return None

            # Take the first ROM file found
            rom_file = rom_files[0]

            # Calculate MD5
            md5_hash = hashlib.md5()
            with zip_ref.open(rom_file) as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest().upper()
    except (zipfile.BadZipFile, KeyError, IOError):
        return None


def filter_roms(roms_folder, json_file):
    """
    Filter ROMs to copy only those with supported hashes into filtered/

    Args:
        roms_folder: Path to the folder containing the ROMs
        json_file: Path to the JSON file with supported hashes
    """
    # Load supported hashes
    with open(json_file, 'r', encoding='utf-8') as f:
        games_data = json.load(f)

    # Create a dict of all supported MD5s with their name
    # And a dict to manage priority per game
    supported_hashes = {}  # MD5 -> file name
    game_priority = {}  # game_id -> best MD5 found

    total_games = len(games_data)

    for game in games_data:
        game_id = game['game_id']
        hashes = game.get('supported_hashes', [])

        # Priority: France > Europe > USA > others
        best_hash = None
        best_priority = -1

        for hash_info in hashes:
            md5 = hash_info.get('MD5', '').upper()
            name = hash_info.get('Name', '')

            if not md5:
                continue

            supported_hashes[md5] = name

            # Determine priority
            priority = 0
            # Look for Fr in parentheses: (Fr), (En,Fr,De), etc.
            if '(France)' in name or ',Fr' in name or '(Fr)' in name or '(Fr,' in name:
                priority = 3
            elif '(Europe)' in name:
                priority = 2
            elif '(USA)' in name:
                priority = 1

            if priority > best_priority:
                best_priority = priority
                best_hash = md5

        # If no priority found, keep all hashes
        if best_hash:
            game_priority[game_id] = best_hash

    print(f"📋 {len(supported_hashes)} supported hashes loaded for {total_games} games\n")

    # Create output folder
    output_folder = Path(roms_folder) / "filtered"
    output_folder.mkdir(exist_ok=True)

    # Scan ROMs
    roms_path = Path(roms_folder)
    rom_files = (list(roms_path.glob("*.z64")) + list(roms_path.glob("*.n64")) +
                 list(roms_path.glob("*.v64")) + list(roms_path.glob("*.zip")))

    print(f"🔍 Analyzing {len(rom_files)} ROMs...\n")

    kept_count = 0
    found_md5s = {}  # game_id -> (MD5, file_path)

    # First pass: find all matching ROMs
    for i, rom_file in enumerate(rom_files, 1):
        print(f"[{i}/{len(rom_files)}] Scanning {rom_file.name}...", end='\r')

        try:
            # Calculate ROM MD5
            if rom_file.suffix.lower() == '.zip':
                md5 = calculate_md5_from_zip(rom_file)
            else:
                md5 = calculate_md5(rom_file)

            if md5 is None:
                continue

            # Check if hash is supported
            if md5 in supported_hashes:
                # Find corresponding game_id
                for game in games_data:
                    for hash_info in game.get('supported_hashes', []):
                        if hash_info.get('MD5', '').upper() == md5:
                            game_id = game['game_id']

                            # Check if we already have a ROM for this game
                            if game_id not in found_md5s:
                                found_md5s[game_id] = (md5, rom_file)
                            else:
                                # Compare with priority
                                best_md5 = game_priority.get(game_id)

                                # If this MD5 has priority, replace it
                                if best_md5 and md5 == best_md5:
                                    found_md5s[game_id] = (md5, rom_file)
                            break

        except (IOError, OSError):
            continue

    print(f"\n\n🎮 {len(found_md5s)} unique games found")
    print("📦 Unzipping and copying...\n")

    # Second pass: copy and unzip selected ROMs
    for i, (game_id, (md5, rom_file)) in enumerate(found_md5s.items(), 1):
        print(f"[{i}/{len(found_md5s)}] Copying {rom_file.name}...", end='\r')

        try:
            if rom_file.suffix.lower() == '.zip':
                # Unzip and extract ROM file
                with zipfile.ZipFile(rom_file, 'r') as zip_ref:
                    rom_files_in_zip = [f for f in zip_ref.namelist()
                                        if f.endswith(('.z64', '.n64', '.v64'))]
                    if rom_files_in_zip:
                        rom_file_in_zip = rom_files_in_zip[0]
                        # Extract directly into filtered folder
                        zip_ref.extract(rom_file_in_zip, output_folder)
                        # Rename if needed to avoid subdirectories
                        extracted_path = output_folder / rom_file_in_zip
                        final_path = output_folder / Path(rom_file_in_zip).name
                        if extracted_path != final_path:
                            extracted_path.rename(final_path)
                        kept_count += 1
            else:
                # Copy directly
                output_path = output_folder / rom_file.name
                shutil.copy2(rom_file, output_path)
                kept_count += 1

        except (zipfile.BadZipFile, IOError, OSError) as error:
            print(f"\n⚠️  Error for {rom_file.name}: {error}")
            continue

    print("\n\n✅ Filtering complete!")
    print(f"✅ {kept_count} ROMs copied (unzipped) to {output_folder}")
    print(f"📊 {kept_count}/{total_games} games from JSON found ({kept_count*100//total_games}%)")
    print(f"⏭️  {len(rom_files) - kept_count} ROMs ignored (remain in original folder)")

    # Display missing games
    missing_games = []
    for game in games_data:
        if game['game_id'] not in found_md5s:
            missing_games.append(game['game_title'])

    if missing_games:
        print(f"\n❌ {len(missing_games)} games not found:")
        for title in sorted(missing_games):
            print(f"   - {title}")


def main():
    """Main entry point for the script"""
    roms_folder = Path("./roms")
    json_file = Path("./data/n64_games_data_light.json")

    print("="*60)
    print("N64 ROM Filtering by Supported Hashes")
    print("="*60)
    print()
    print(f"ROMs folder: {roms_folder}")
    print(f"JSON file: {json_file}")
    print()

    filter_roms(str(roms_folder), str(json_file))


if __name__ == "__main__":
    main()
