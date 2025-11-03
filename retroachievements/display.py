"""
Display functions for results
"""


def display_game_info(game_info: dict):
    """
    Display game information

    Args:
        game_info: Dictionary containing game information
    """
    print("="*60)
    print(f"Game: {game_info.get('Title', 'N/A')}")
    print(f"Console: {game_info.get('ConsoleName', 'N/A')}")
    print(f"Publisher: {game_info.get('Publisher', 'N/A')}")
    print(f"Developer: {game_info.get('Developer', 'N/A')}")
    print(f"Genre: {game_info.get('Genre', 'N/A')}")
    print(f"Release Date: {game_info.get('Released', 'N/A')}")
    print("="*60)


def display_supported_hashes(hashes: list):
    """
    Display supported versions (hashes)

    Args:
        hashes: List of hashes
    """
    print("\n=== SUPPORTED VERSIONS (Hashes) ===\n")

    if hashes:
        for i, hash_info in enumerate(hashes, 1):
            print(f"\n{i}. {hash_info.get('Name', 'N/A')}")
            print(f"   MD5: {hash_info.get('MD5', 'N/A')}")

            labels = hash_info.get('Labels', [])
            if labels:
                print(f"   Labels: {', '.join(labels)}")

            patch_url = hash_info.get('PatchUrl')
            if patch_url:
                print(f"   Patch: {patch_url}")
    else:
        print("No supported versions found")


def display_search_results(matches: list):
    """
    Display search results

    Args:
        matches: List of games found
    """
    if not matches:
        print("❌ No game found with this name")
        return None

    print(f"✅ {len(matches)} game(s) found:\n")
    for game in matches:
        print(f"  - {game['Title']} (ID: {game['ID']})")

    return matches[0]
