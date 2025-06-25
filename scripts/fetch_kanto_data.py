#!/usr/bin/env python3
"""
Script to fetch Kanto region data from PokéAPI and structure it for BeTheMC.
"""
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

class KantoDataFetcher:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.data_dir = project_root / "data" / "raw" / "kanto"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch data with retry logic."""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        return {}

    def fetch_kanto_locations(self) -> List[Dict[str, Any]]:
        """Fetch all Kanto locations."""
        logger.info("Fetching Kanto locations...")
        
        # Get Kanto region data
        region_data = self.fetch_with_retry(f"{self.base_url}/region/1/")
        locations = []
        
        for location_info in region_data.get("locations", []):
            location_name = location_info["name"]
            location_url = location_info["url"]
            
            # Get detailed location info
            location_detail = self.fetch_with_retry(location_url)
            
            location_data = {
                "id": location_detail["id"],
                "name": location_detail["name"],
                "display_name": self._get_display_name(location_detail["names"]),
                "description": self._get_location_description(location_detail["name"]),
                "areas": [
                    {
                        "id": area["name"],
                        "name": area["name"],
                        "encounters": self._get_encounters(area["url"])
                    }
                    for area in location_detail.get("areas", [])
                ],
                "connected_locations": self._get_connected_locations(location_detail["name"]),
                "services": self._get_location_services(location_detail["name"]),
                "notable_features": self._get_notable_features(location_detail["name"])
            }
            
            locations.append(location_data)
            logger.info(f"Fetched location: {location_data['display_name']}")
            time.sleep(0.1)  # Be nice to the API
            
        return locations

    def _get_display_name(self, names: List[Dict[str, Any]]) -> str:
        """Get the English display name from the names list."""
        for name_info in names:
            if name_info["language"]["name"] == "en":
                return name_info["name"]
        return "Unknown Location"

    def fetch_kanto_pokemon(self) -> List[Dict[str, Any]]:
        """Fetch all Kanto Pokémon (1-151)."""
        logger.info("Fetching Kanto Pokémon...")
        
        pokemon_list = []
        for pokemon_id in range(1, 152):  # Kanto Pokémon are 1-151
            try:
                pokemon_data = self.fetch_with_retry(f"{self.base_url}/pokemon/{pokemon_id}/")
                
                pokemon_info = {
                    "id": pokemon_data["id"],
                    "name": pokemon_data["name"],
                    "display_name": pokemon_data["name"].title(),
                    "types": [t["type"]["name"] for t in pokemon_data["types"]],
                    "height": pokemon_data["height"] / 10,  # Convert to meters
                    "weight": pokemon_data["weight"] / 10,  # Convert to kg
                    "abilities": [
                        {
                            "name": ability["ability"]["name"],
                            "is_hidden": ability["is_hidden"]
                        }
                        for ability in pokemon_data["abilities"]
                    ],
                    "stats": {
                        stat["stat"]["name"]: stat["base_stat"]
                        for stat in pokemon_data["stats"]
                    },
                    "moves": [
                        move["move"]["name"]
                        for move in pokemon_data["moves"][:10]  # Limit to first 10 moves
                    ],
                    "sprites": {
                        "front_default": pokemon_data["sprites"]["front_default"],
                        "back_default": pokemon_data["sprites"]["back_default"]
                    }
                }
                
                pokemon_list.append(pokemon_info)
                logger.info(f"Fetched Pokémon: {pokemon_info['display_name']}")
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to fetch Pokémon {pokemon_id}: {e}")
                
        return pokemon_list

    def fetch_kanto_characters(self) -> List[Dict[str, Any]]:
        """Create Kanto character data (Gym Leaders, NPCs, etc.)."""
        logger.info("Creating Kanto character data...")
        
        # This is manual data since PokéAPI doesn't have character info
        characters = [
            {
                "id": "professor_oak",
                "name": "Professor Oak",
                "title": "Pokémon Professor",
                "location": "Pallet Town",
                "description": "The renowned Pokémon Professor who gives new trainers their first Pokémon and Pokédex.",
                "personality": "Wise, knowledgeable, slightly forgetful",
                "role": "mentor"
            },
            {
                "id": "red",
                "name": "Red",
                "title": "Pokémon Champion",
                "location": "Indigo Plateau",
                "description": "The silent protagonist who became the youngest Pokémon Champion in history.",
                "personality": "Silent, determined, skilled",
                "role": "rival_champion"
            },
            {
                "id": "blue",
                "name": "Blue",
                "title": "Pokémon Champion",
                "location": "Various",
                "description": "Red's rival and grandson of Professor Oak. A confident and competitive trainer.",
                "personality": "Confident, competitive, sometimes arrogant",
                "role": "rival"
            },
            {
                "id": "brock",
                "name": "Brock",
                "title": "Pewter City Gym Leader",
                "location": "Pewter City",
                "description": "The Rock-type Gym Leader of Pewter City. A caring trainer who loves Pokémon.",
                "personality": "Caring, knowledgeable about Pokémon, loves cooking",
                "role": "gym_leader"
            },
            {
                "id": "misty",
                "name": "Misty",
                "title": "Cerulean City Gym Leader",
                "location": "Cerulean City",
                "description": "The Water-type Gym Leader of Cerulean City. Feisty and protective of her sisters.",
                "personality": "Feisty, protective, loves Water Pokémon",
                "role": "gym_leader"
            },
            {
                "id": "lt_surge",
                "name": "Lt. Surge",
                "title": "Vermilion City Gym Leader",
                "location": "Vermilion City",
                "description": "The Electric-type Gym Leader of Vermilion City. A former military officer.",
                "personality": "Tough, military-minded, values strength",
                "role": "gym_leader"
            },
            {
                "id": "erika",
                "name": "Erika",
                "title": "Celadon City Gym Leader",
                "location": "Celadon City",
                "description": "The Grass-type Gym Leader of Celadon City. A graceful and elegant trainer.",
                "personality": "Graceful, elegant, loves flowers",
                "role": "gym_leader"
            },
            {
                "id": "koga",
                "name": "Koga",
                "title": "Fuchsia City Gym Leader",
                "location": "Fuchsia City",
                "description": "The Poison-type Gym Leader of Fuchsia City. A ninja master.",
                "personality": "Mysterious, disciplined, ninja-like",
                "role": "gym_leader"
            },
            {
                "id": "sabrina",
                "name": "Sabrina",
                "title": "Saffron City Gym Leader",
                "location": "Saffron City",
                "description": "The Psychic-type Gym Leader of Saffron City. A powerful psychic.",
                "personality": "Mysterious, powerful, psychic abilities",
                "role": "gym_leader"
            },
            {
                "id": "blaine",
                "name": "Blaine",
                "title": "Cinnabar Island Gym Leader",
                "location": "Cinnabar Island",
                "description": "The Fire-type Gym Leader of Cinnabar Island. A scientist and quiz master.",
                "personality": "Intelligent, loves riddles, scientific mind",
                "role": "gym_leader"
            },
            {
                "id": "giovanni",
                "name": "Giovanni",
                "title": "Viridian City Gym Leader",
                "location": "Viridian City",
                "description": "The Ground-type Gym Leader of Viridian City and leader of Team Rocket.",
                "personality": "Ruthless, ambitious, criminal mastermind",
                "role": "gym_leader_villain"
            }
        ]
        
        return characters

    def fetch_story_elements(self) -> List[Dict[str, Any]]:
        """Create story elements and plot hooks for Kanto."""
        logger.info("Creating story elements...")
        
        story_elements = [
            {
                "id": "team_rocket_plot",
                "name": "Team Rocket Conspiracy",
                "description": "Team Rocket is stealing Pokémon and causing trouble across Kanto.",
                "locations": ["Cerulean City", "Lavender Town", "Saffron City"],
                "characters": ["Giovanni", "Jessie", "James"],
                "type": "main_plot"
            },
            {
                "id": "pokemon_league_challenge",
                "name": "Pokémon League Challenge",
                "description": "The ultimate goal of becoming the Pokémon Champion.",
                "locations": ["Indigo Plateau"],
                "characters": ["Red", "Blue", "Elite Four"],
                "type": "main_plot"
            },
            {
                "id": "mewtwo_legend",
                "name": "Mewtwo Legend",
                "description": "Rumors of a powerful cloned Pokémon created by scientists.",
                "locations": ["Cinnabar Island", "Cerulean Cave"],
                "characters": ["Scientists", "Mewtwo"],
                "type": "side_plot"
            },
            {
                "id": "pokemon_tower_ghosts",
                "name": "Pokémon Tower Ghosts",
                "description": "The haunted Pokémon Tower in Lavender Town.",
                "locations": ["Lavender Town"],
                "characters": ["Ghost Pokémon", "Mr. Fuji"],
                "type": "side_plot"
            },
            {
                "id": "safari_zone_adventure",
                "name": "Safari Zone Adventure",
                "description": "Exploring the Safari Zone to catch rare Pokémon.",
                "locations": ["Fuchsia City"],
                "characters": ["Safari Zone Warden"],
                "type": "side_plot"
            }
        ]
        
        return story_elements

    def _get_location_description(self, location_name: str) -> str:
        """Get a description for a location."""
        descriptions = {
            "pallet-town": "A peaceful town where many Pokémon trainers begin their journey. Home to Professor Oak's laboratory.",
            "viridian-city": "A bustling city with the first Pokémon Center and Mart. The Viridian Gym is temporarily closed.",
            "pewter-city": "A city known for its museum and the first official Gym. Brock leads the Rock-type Gym here.",
            "cerulean-city": "A coastal city with a beautiful bridge. Misty leads the Water-type Gym here.",
            "vermilion-city": "A port city with a famous lighthouse. Lt. Surge leads the Electric-type Gym here.",
            "lavender-town": "A quiet town known for the Pokémon Tower, where deceased Pokémon are laid to rest.",
            "celadon-city": "A large city with a department store and casino. Erika leads the Grass-type Gym here.",
            "saffron-city": "A major city with the Fighting Dojo and Psychic Gym. Sabrina leads the Psychic-type Gym here.",
            "fuchsia-city": "A city with the Safari Zone and Pokémon Center. Koga leads the Poison-type Gym here.",
            "cinnabar-island": "An island with a volcano and research lab. Blaine leads the Fire-type Gym here.",
            "indigo-plateau": "The location of the Pokémon League and Elite Four. The ultimate challenge for trainers."
        }
        return descriptions.get(location_name, f"A location in the Kanto region.")

    def _get_connected_locations(self, location_name: str) -> List[str]:
        """Get connected locations for a given location."""
        connections = {
            "pallet-town": ["Route 1"],
            "viridian-city": ["Route 1", "Route 2", "Route 22"],
            "pewter-city": ["Route 2", "Route 3"],
            "cerulean-city": ["Route 4", "Route 5", "Route 24", "Route 25"],
            "vermilion-city": ["Route 6", "Route 11"],
            "lavender-town": ["Route 8", "Route 10", "Route 12"],
            "celadon-city": ["Route 7", "Route 16"],
            "saffron-city": ["Route 5", "Route 6", "Route 7", "Route 8"],
            "fuchsia-city": ["Route 15", "Route 18", "Route 19"],
            "cinnabar-island": ["Route 21"],
            "indigo-plateau": ["Route 23"]
        }
        return connections.get(location_name, [])

    def _get_location_services(self, location_name: str) -> List[str]:
        """Get available services at a location."""
        services = {
            "pallet-town": ["Professor Oak's Lab"],
            "viridian-city": ["Pokémon Center", "Pokémon Mart", "Gym (closed)"],
            "pewter-city": ["Pokémon Center", "Pokémon Mart", "Museum", "Gym"],
            "cerulean-city": ["Pokémon Center", "Pokémon Mart", "Gym"],
            "vermilion-city": ["Pokémon Center", "Pokémon Mart", "Gym", "Lighthouse"],
            "lavender-town": ["Pokémon Center", "Pokémon Tower"],
            "celadon-city": ["Pokémon Center", "Department Store", "Casino", "Gym"],
            "saffron-city": ["Pokémon Center", "Fighting Dojo", "Gym"],
            "fuchsia-city": ["Pokémon Center", "Safari Zone", "Gym"],
            "cinnabar-island": ["Pokémon Center", "Research Lab", "Gym"],
            "indigo-plateau": ["Pokémon League", "Elite Four"]
        }
        return services.get(location_name, [])

    def _get_notable_features(self, location_name: str) -> List[str]:
        """Get notable features of a location."""
        features = {
            "pallet-town": ["Professor Oak's Laboratory", "Peaceful atmosphere"],
            "viridian-city": ["First major city", "Closed gym mystery"],
            "pewter-city": ["Pokémon Museum", "Rock-type gym"],
            "cerulean-city": ["Nugget Bridge", "Water-type gym"],
            "vermilion-city": ["S.S. Anne", "Electric-type gym"],
            "lavender-town": ["Pokémon Tower", "Haunted atmosphere"],
            "celadon-city": ["Department Store", "Game Corner", "Grass-type gym"],
            "saffron-city": ["Silph Co.", "Fighting Dojo", "Psychic-type gym"],
            "fuchsia-city": ["Safari Zone", "Poison-type gym"],
            "cinnabar-island": ["Volcano", "Research Lab", "Fire-type gym"],
            "indigo-plateau": ["Pokémon League", "Elite Four", "Champion's room"]
        }
        return features.get(location_name, [])

    def _get_encounters(self, area_url: str) -> List[Dict[str, Any]]:
        """Get Pokémon encounters for an area."""
        try:
            area_data = self.fetch_with_retry(area_url)
            encounters = []
            
            for encounter in area_data.get("pokemon_encounters", []):
                pokemon = encounter["pokemon"]
                encounter_info = {
                    "pokemon": pokemon["name"],
                    "encounter_methods": [
                        method["encounter_method"]["name"]
                        for method in encounter["version_details"][0]["encounter_details"]
                    ]
                }
                encounters.append(encounter_info)
                
            return encounters
        except Exception as e:
            logger.warning(f"Failed to get encounters for {area_url}: {e}")
            return []

    def save_data(self, data: List[Dict[str, Any]], filename: str):
        """Save data to JSON file."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} items to {filepath}")

    def fetch_all_data(self):
        """Fetch all Kanto data."""
        logger.info("Starting Kanto data fetch...")
        
        try:
            # Fetch locations
            locations = self.fetch_kanto_locations()
            self.save_data(locations, "locations.json")
            
            # Fetch Pokémon
            pokemon = self.fetch_kanto_pokemon()
            self.save_data(pokemon, "pokemon.json")
            
            # Create characters
            characters = self.fetch_kanto_characters()
            self.save_data(characters, "characters.json")
            
            # Create story elements
            story_elements = self.fetch_story_elements()
            self.save_data(story_elements, "story_elements.json")
            
            logger.info("All Kanto data fetched successfully!")
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise

def main():
    """Main function."""
    fetcher = KantoDataFetcher()
    fetcher.fetch_all_data()

if __name__ == "__main__":
    main() 