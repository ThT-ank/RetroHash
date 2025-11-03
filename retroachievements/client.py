"""
Client for RetroAchievements.org API
"""
import requests
from typing import Optional


class RetroAchievementsAPI:
    """Client for RetroAchievements API"""
    
    BASE_URL = "https://retroachievements.org/API"
    
    def __init__(self, username: str, api_key: str):
        """
        Initialize API client
        
        Args:
            username: Your RetroAchievements username
            api_key: Your API key (available on your profile)
        """
        self.username = username
        self.api_key = api_key
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a request to the API"""
        if params is None:
            params = {}
        
        # Add credentials
        params['z'] = self.username
        params['y'] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_game_info(self, game_id: int) -> dict:
        """
        Get detailed game information
        
        Args:
            game_id: The game ID on RetroAchievements
        
        Returns:
            Dictionary containing game information
        """
        return self._make_request("API_GetGameExtended.php", {'i': game_id})
    
    def get_game_hashes(self, game_id: int) -> list:
        """
        Get supported ROM hashes for a game
        
        Args:
            game_id: The game ID
        
        Returns:
            List of supported hashes with their info (MD5, Name, Labels, PatchUrl)
        """
        data = self._make_request("API_GetGameHashes.php", {'i': game_id})
        if 'Results' in data:
            return data['Results']
        return []
    
    def get_game_list(self, console_id: int, with_achievements: bool = True) -> list:
        """
        Get game list for a console
        
        Args:
            console_id: The console ID (2 = Nintendo 64)
            with_achievements: If True, only return games with achievements
        
        Returns:
            List of games
        """
        params = {'i': console_id}
        if with_achievements:
            params['f'] = 1
        
        data = self._make_request("API_GetGameList.php", params)
        return data if isinstance(data, list) else []
    
    def search_game(self, game_name: str, console_id: int = 2) -> list:
        """
        Search for a game by name on a console
        
        Args:
            game_name: Name of the game to search for
            console_id: ID of the console (2 = Nintendo 64 by default)
        
        Returns:
            List of matching games
        """
        games = self.get_game_list(console_id)
        game_name_lower = game_name.lower()
        
        matches = [
            game for game in games 
            if game_name_lower in game.get('Title', '').lower()
        ]
        
        return matches
