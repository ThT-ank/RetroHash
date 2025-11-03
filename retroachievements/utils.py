"""
Utility functions
"""
import json


def save_to_json(data: dict, filename: str):
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        filename: File name
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Complete data saved to {filename}")


def remove_achievements(data: dict) -> dict:
    """
    Remove the Achievements field from a data dictionary
    
    Args:
        data: Dictionary potentially containing an Achievements field
        
    Returns:
        Dictionary without the Achievements field
    """
    import copy
    data_copy = copy.deepcopy(data)
    
    if 'game_info' in data_copy and 'Achievements' in data_copy['game_info']:
        del data_copy['game_info']['Achievements']
    
    return data_copy
