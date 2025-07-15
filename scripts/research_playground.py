#!/usr/bin/env python3
"""
Research playground for experimenting with advanced storytelling techniques.
"""
import sys
from pathlib import Path
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class StoryResearchPlayground:
    """Research playground for advanced storytelling experiments."""
    
    def __init__(self):
        """Initialize the research playground."""
        self.client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def experiment_character_relationships(self):
        """Experiment with character relationship dynamics."""
        print("🔬 Experiment 1: Character Relationship Dynamics")
        print("=" * 50)
        
        # Get all characters
        character_results = self.client.search(
            collection_name="kanto_knowledge",
            query_vector=self.embedder.encode(["character personality traits"])[0].tolist(),
            limit=10,
            query_filter={"must": [{"key": "type", "match": {"value": "character"}}]}
        )
        
        characters = []
        for result in character_results:
            payload = result.payload
            characters.append({
                "name": payload.get("name", "Unknown"),
                "personality": payload.get("text", ""),
                "score": result.score
            })
        
        print(f"Found {len(characters)} characters for relationship analysis")
        
        # Analyze potential relationships
        relationships = []
        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters[i+1:], i+1):
                # Simple relationship analysis based on personality compatibility
                relationship_type = self._analyze_relationship(char1, char2)
                relationships.append({
                    "character1": char1["name"],
                    "character2": char2["name"],
                    "relationship": relationship_type,
                    "potential_story": self._generate_relationship_story(char1, char2, relationship_type)
                })
        
        # Display interesting relationships
        print("\n🌟 Interesting Character Relationships:")
        for rel in relationships[:5]:  # Show top 5
            print(f"\n{rel['character1']} ↔ {rel['character2']}")
            print(f"Relationship: {rel['relationship']}")
            print(f"Story Potential: {rel['potential_story'][:100]}...")
    
    def experiment_location_atmosphere(self):
        """Experiment with location-based atmosphere generation."""
        print("\n🔬 Experiment 2: Location Atmosphere Generation")
        print("=" * 50)
        
        # Get locations with different characteristics
        location_queries = [
            "mysterious haunted location",
            "bright cheerful city",
            "dangerous wild area",
            "peaceful nature setting"
        ]
        
        for query in location_queries:
            results = self.client.search(
                collection_name="kanto_knowledge",
                query_vector=self.embedder.encode([query])[0].tolist(),
                limit=3,
                query_filter={"must": [{"key": "type", "match": {"value": "location"}}]}
            )
            
            print(f"\n🎯 Query: '{query}'")
            for result in results:
                payload = result.payload
                print(f"  • {payload.get('name', 'Unknown')} (Score: {result.score:.3f})")
                print(f"    Atmosphere: {payload.get('text', '')[:100]}...")
    
    def experiment_pokemon_personality_stories(self):
        """Experiment with Pokémon personality-driven stories."""
        print("\n🔬 Experiment 3: Pokémon Personality Stories")
        print("=" * 50)
        
        # Get Pokémon with personalities
        pokemon_results = self.client.search(
            collection_name="kanto_knowledge",
            query_vector=self.embedder.encode(["pokemon personality temperament"])[0].tolist(),
            limit=5,
            query_filter={"must": [{"key": "type", "match": {"value": "pokemon"}}]}
        )
        
        print("Found Pokémon with personalities:")
        for result in pokemon_results:
            payload = result.payload
            print(f"\n🎯 {payload.get('display_name', 'Unknown')}")
            print(f"   Personality: {payload.get('text', '')[:150]}...")
            
            # Generate personality-based story scenarios
            scenarios = self._generate_pokemon_scenarios(payload)
            print(f"   Story Scenarios:")
            for i, scenario in enumerate(scenarios, 1):
                print(f"     {i}. {scenario}")
    
    def experiment_seasonal_storytelling(self):
        """Experiment with seasonal storytelling elements."""
        print("\n🔬 Experiment 4: Seasonal Storytelling")
        print("=" * 50)
        
        seasons = ["spring", "summer", "autumn", "winter"]
        
        for season in seasons:
            print(f"\n🌸 {season.title()} Story Elements:")
            
            # Generate seasonal atmosphere
            atmosphere = self._generate_seasonal_atmosphere(season)
            print(f"   Atmosphere: {atmosphere}")
            
            # Generate seasonal events
            events = self._generate_seasonal_events(season)
            print(f"   Events: {', '.join(events)}")
            
            # Generate seasonal Pokémon encounters
            encounters = self._generate_seasonal_encounters(season)
            print(f"   Encounters: {', '.join(encounters)}")
    
    def experiment_emotional_story_arcs(self):
        """Experiment with emotional story arc generation."""
        print("\n🔬 Experiment 5: Emotional Story Arcs")
        print("=" * 50)
        
        emotional_arcs = [
            "friendship_development",
            "overcoming_fear", 
            "learning_responsibility",
            "finding_identity",
            "sacrifice_and_growth"
        ]
        
        for arc in emotional_arcs:
            print(f"\n💖 {arc.replace('_', ' ').title()} Arc:")
            
            # Generate arc structure
            structure = self._generate_emotional_arc(arc)
            for i, stage in enumerate(structure, 1):
                print(f"   Stage {i}: {stage}")
    
    def _analyze_relationship(self, char1, char2):
        """Analyze potential relationship between two characters."""
        # Simple personality-based relationship analysis
        personality1 = char1["personality"].lower()
        personality2 = char2["personality"].lower()
        
        if "caring" in personality1 and "caring" in personality2:
            return "Mutual Caregivers"
        elif "competitive" in personality1 and "competitive" in personality2:
            return "Friendly Rivals"
        elif "mysterious" in personality1 and "curious" in personality2:
            return "Mystery Seeker"
        elif "wise" in personality1 and "young" in personality2:
            return "Mentor-Student"
        else:
            return "Potential Friends"
    
    def _generate_relationship_story(self, char1, char2, relationship_type):
        """Generate a story based on character relationship."""
        stories = {
            "Mutual Caregivers": f"{char1['name']} and {char2['name']} work together to help others",
            "Friendly Rivals": f"{char1['name']} and {char2['name']} push each other to grow stronger",
            "Mystery Seeker": f"{char2['name']} is drawn to {char1['name']}'s mysterious nature",
            "Mentor-Student": f"{char1['name']} guides {char2['name']} on their journey",
            "Potential Friends": f"{char1['name']} and {char2['name']} discover they have more in common than expected"
        }
        return stories.get(relationship_type, "An interesting dynamic develops between them")
    
    def _generate_pokemon_scenarios(self, pokemon_data):
        """Generate story scenarios based on Pokémon personality."""
        scenarios = []
        
        personality = pokemon_data.get("text", "").lower()
        
        if "loyal" in personality:
            scenarios.append("Proves loyalty in a crisis")
        if "brave" in personality:
            scenarios.append("Faces a fear to protect others")
        if "nurturing" in personality:
            scenarios.append("Cares for injured Pokémon")
        if "independent" in personality:
            scenarios.append("Learns to work with others")
        if "playful" in personality:
            scenarios.append("Brings joy to a serious situation")
        
        return scenarios[:3]  # Return top 3 scenarios
    
    def _generate_seasonal_atmosphere(self, season):
        """Generate seasonal atmosphere descriptions."""
        atmospheres = {
            "spring": "Renewal and new beginnings fill the air",
            "summer": "Warm energy and adventure beckon",
            "autumn": "Golden light and gentle nostalgia",
            "winter": "Quiet reflection and inner strength"
        }
        return atmospheres.get(season, "Seasonal changes affect the world")
    
    def _generate_seasonal_events(self, season):
        """Generate seasonal events."""
        events = {
            "spring": ["Cherry Blossom Festival", "Pokémon Breeding Season"],
            "summer": ["Fire Festival", "Beach Tournament"],
            "autumn": ["Harvest Festival", "Ghost Type Awakening"],
            "winter": ["Winter Solstice", "Ice Cave Expedition"]
        }
        return events.get(season, ["Seasonal gathering"])
    
    def _generate_seasonal_encounters(self, season):
        """Generate seasonal Pokémon encounters."""
        encounters = {
            "spring": ["Grass types", "Baby Pokémon", "Migrating birds"],
            "summer": ["Fire types", "Water types", "Beach Pokémon"],
            "autumn": ["Ghost types", "Harvest Pokémon", "Preparing for winter"],
            "winter": ["Ice types", "Hibernating Pokémon", "Winter-adapted species"]
        }
        return encounters.get(season, ["Seasonal Pokémon"])
    
    def _generate_emotional_arc(self, arc_type):
        """Generate emotional story arc structure."""
        arcs = {
            "friendship_development": [
                "Initial meeting and misunderstanding",
                "Shared experience creates bond",
                "Conflict tests the friendship",
                "Reconciliation and stronger bond"
            ],
            "overcoming_fear": [
                "Character faces their fear",
                "Fear seems overwhelming",
                "Support from friends and Pokémon",
                "Courage triumphs over fear"
            ],
            "learning_responsibility": [
                "Character avoids responsibility",
                "Consequences of their actions",
                "Understanding the impact on others",
                "Embracing responsibility with pride"
            ],
            "finding_identity": [
                "Character questions who they are",
                "Trying to be someone else",
                "Discovering their true strengths",
                "Embracing their unique identity"
            ],
            "sacrifice_and_growth": [
                "Character must give up something important",
                "Struggle with the decision",
                "Making the sacrifice for others",
                "Growth through selflessness"
            ]
        }
        return arcs.get(arc_type, ["Story development", "Character growth", "Resolution"])

def main():
    """Run the research playground experiments."""
    playground = StoryResearchPlayground()
    
    print("🧪 Advanced Storytelling Research Playground")
    print("=" * 60)
    
    # Run experiments
    playground.experiment_character_relationships()
    playground.experiment_location_atmosphere()
    playground.experiment_pokemon_personality_stories()
    playground.experiment_seasonal_storytelling()
    playground.experiment_emotional_story_arcs()
    
    print("\n✅ Research experiments complete!")
    print("\nThese experiments demonstrate:")
    print("• Character relationship dynamics")
    print("• Location-based atmosphere generation")
    print("• Pokémon personality-driven stories")
    print("• Seasonal storytelling elements")
    print("• Emotional story arc structures")

if __name__ == "__main__":
    main() 