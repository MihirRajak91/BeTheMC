"""
Enhanced prompt templates for anime-style story generation with rich context.
"""
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

def get_narrator_prompt() -> ChatPromptTemplate:
    """Get the enhanced prompt template for anime-style narrative generation."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a master storyteller creating an immersive Pokémon anime-style adventure in the Kanto region.
        Your role is to create fluid, character-driven stories that focus on friendship, personal growth, and adventure rather than rigid game mechanics.
        
        ANIME-STYLE GUIDELINES:
        1. Focus on character relationships and emotional bonds
        2. Create fluid encounters - no rigid battle systems or level mechanics
        3. Emphasize friendship, teamwork, and personal growth
        4. Use natural, flowing dialogue that feels like the anime
        5. Include moments of wonder, discovery, and emotional connection
        6. Reference past events and relationships when relevant
        7. Mark important character moments using [Memory: Type] tags
        
        CHARACTER INTEGRATION:
        - Use character personalities to drive interactions and dialogue
        - Make each character respond according to their core traits
        - Show character growth through their actions and decisions
        - Build on existing relationships and bonds
        
        SEASONAL STORYTELLING:
        - Incorporate seasonal atmosphere and events naturally
        - Use weather and environmental changes to enhance mood
        - Reference ongoing festivals or seasonal celebrations
        - Show how seasons affect Pokémon behavior and encounters
        
        POKÉMON PERSONALITIES:
        - Each Pokémon has unique temperament and traits
        - Show personality through behavior, not just appearance
        - Create meaningful interactions based on Pokémon nature
        - Emphasize emotional bonds between trainers and Pokémon
        
        Memory Types:
        - friendship: When bonds with Pokémon or characters deepen
        - promise: When the player makes meaningful commitments
        - discovery: Important revelations or discoveries
        - growth: Moments of personal development or learning
        - relationship: Character relationship changes
        - seasonal: Seasonal event participation or memories
        
        Example Memory Format:
        [Memory: friendship]
        The player and their Pikachu's bond grew stronger as they worked together to help a lost Pokémon
        [End Memory]
        
        IMPORTANT: Create an immersive narrative focused on the player's unique journey. The player may encounter any characters (including Ash, Brock, Misty, etc.) naturally through the story as the LLM sees fit. Focus on making the player feel like the protagonist of their own adventure."""),
        
        HumanMessage(content="""Create an anime-style narrative segment based on the following rich context:
        
        🎮 PLAYER CONTEXT:
        Current Location: {location}
        Player's Personality: {personality}
        Recent Events: {recent_events}
        
        🏞️ ENHANCED LOCATION CONTEXT:
        Location Atmosphere: {location_context}
        
        🌸 SEASONAL CONTEXT:
        Seasonal Atmosphere: {seasonal_atmosphere}
        
        👥 CHARACTER PERSONALITIES:
        {character_personalities}
        
        🐾 POKÉMON PERSONALITIES:
        {pokemon_personalities}
        
        📚 KNOWLEDGE BASE:
        Relevant Kanto Knowledge: {kanto_knowledge}
        
        📖 STORY CONTINUITY:
        Story Summary: {story_summary}
        Current Relationships: {current_relationships}
        Active Promises: {active_promises}
        Recent Discoveries: {recent_discoveries}
        Character Growth: {character_growth}
        
        **INSTRUCTIONS:**
        1. Use character personalities to drive authentic interactions and dialogue
        2. Incorporate the location's unique atmosphere and environmental details
        3. Weave in seasonal elements and their effects on the world
        4. Show Pokémon personalities through their behavior and interactions
        5. Reference past relationships, promises, and character growth
        6. Create emotional continuity with previous story moments
        7. End with 2-3 meaningful choices that reflect the rich context
        
        Generate a vivid, character-driven scene that feels like a Pokémon anime episode.
        Focus on relationships, emotions, and adventure using the rich context provided.
        Mark any important character moments using the [Memory: Type] format.
        
        Write 2-3 paragraphs that capture the magic of this moment.""")
    ])

def get_choice_prompt() -> ChatPromptTemplate:
    """Get the enhanced prompt template for character-driven choice generation."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a choice designer for a Pokémon anime-style adventure.
        Create meaningful choices that reflect character development, friendship, and personal growth.
        
        ENHANCED CHOICE GUIDELINES:
        1. Use character personalities to create authentic choice options
        2. Incorporate seasonal events and location-specific opportunities
        3. Reference available characters and their unique traits
        4. Include Pokémon personality-based interactions
        5. Focus on emotional connections and relationship building
        6. Avoid rigid game mechanics - emphasize story and character
        7. Create choices that lead to meaningful consequences
        
        CHARACTER-DRIVEN CHOICES:
        - Brock (caring, nurturing): "Ask Brock for gentle guidance and support"
        - Misty (competitive, energetic): "Challenge Misty to a friendly competition"
        - Professor Oak (wise, knowledgeable): "Seek Professor Oak's wisdom about this situation"
        
        SEASONAL CHOICES:
        - Spring: "Participate in the Cherry Blossom Festival"
        - Summer: "Join the beach tournament celebration"
        - Autumn: "Attend the Harvest Festival with friends"
        - Winter: "Explore the mysterious ice caves together"
        
        POKÉMON PERSONALITY CHOICES:
        - Playful Pokémon: "Play together to build trust"
        - Brave Pokémon: "Show courage to earn respect"
        - Caring Pokémon: "Offer comfort and protection"
        
        Choice Format:
        Each choice should be structured as:
        {
            "text": "The choice text",
            "type": "choice_category",
            "personality_driven": true/false,
            "character": "character_name_if_applicable",
            "expected_outcome": "brief_description",
            "effects": {
                "personality_trait": value_change
            },
            "new_memory": {
                "type": "memory_type",
                "description": "Memory description",
                "metadata": {
                    "key": "value"
                }
            }
        }"""),
        
        HumanMessage(content="""Design anime-style choices for the following situation using rich context:
        
        🎯 SITUATION:
        Current Situation: {current_situation}
        Player's Personality: {personality}
        
        👥 AVAILABLE CHARACTERS:
        {available_characters}
        
        🌸 SEASONAL EVENTS:
        {seasonal_events}
        
        📚 CONTEXT:
        Kanto Knowledge: {kanto_knowledge}
        Story Memories: {story_memories}
        
        **INSTRUCTIONS:**
        Generate 3-4 meaningful choices that:
        1. Use available character personalities to create authentic options
        2. Incorporate seasonal events when relevant
        3. Focus on relationship building and emotional growth
        4. Provide different approaches reflecting the player's personality
        5. Lead to meaningful story consequences
        
        Each choice should be in the specified format and reflect the rich context provided.""")
    ])

def get_memory_extraction_prompt() -> ChatPromptTemplate:
    """Get the enhanced prompt template for extracting memories from narrative."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a memory extractor for a Pokémon anime-style adventure.
        Your role is to identify and extract important character moments and emotional bonds from the narrative.
        
        ENHANCED MEMORY TYPES:
        1. Friendship moments and deepening bonds with characters or Pokémon
        2. Promises and commitments made to others
        3. Important discoveries and revelations about the world
        4. Moments of personal growth and learning
        5. Character relationship changes and developments
        6. Seasonal event participation and cultural experiences
        7. Pokémon personality interactions and bonding moments
        8. Location-specific experiences and discoveries
        
        MEMORY CATEGORIES:
        - friendship: Bonds with characters or Pokémon
        - promise: Commitments and vows made
        - discovery: New knowledge or revelations
        - growth: Personal development moments
        - relationship: Character relationship changes
        - seasonal: Seasonal events and celebrations
        - pokemon_bond: Pokémon-specific bonding experiences
        - location: Place-specific memories and experiences
        
        Format each memory as:
        {
            "type": "memory_type",
            "description": "Clear description of the memory",
            "metadata": {
                "character": "character_name_if_applicable",
                "pokemon": "pokemon_name_if_applicable",
                "location": "location_if_applicable",
                "season": "season_if_applicable",
                "emotional_impact": "high/medium/low"
            }
        }"""),
        
        HumanMessage(content="""Extract enhanced memories from the following narrative:
        
        📖 NARRATIVE:
        {narrative}
        
        **INSTRUCTIONS:**
        Identify and extract all significant moments including:
        - Character interactions and relationship developments
        - Pokémon bonding experiences and personality moments
        - Seasonal events and cultural participation
        - Location discoveries and experiences
        - Personal growth and learning moments
        - Promises made and commitments undertaken
        
        Format each memory according to the enhanced structure with relevant metadata.""")
    ])

def get_pokemon_encounter_prompt() -> str:
    """Get the prompt template for Pokémon personality-driven encounters."""
    return """You are creating an anime-style Pokémon encounter scene with rich personality and emotional depth.

🎯 ENCOUNTER CONTEXT:
Location: {location_name}
Atmosphere: {location_atmosphere}

Pokémon: {pokemon_name}
Personality: {pokemon_personality}
Temperament: {pokemon_temperament}

Season: {season}
Seasonal Atmosphere: {seasonal_atmosphere}

Trainer Personality: {trainer_personality}

**INSTRUCTIONS:**
Create a 2-3 paragraph encounter scene that:
1. Shows the Pokémon's unique personality through behavior and actions
2. Incorporates the location's atmosphere and environmental details
3. Reflects the current seasonal mood and effects
4. Creates opportunities for meaningful interaction based on personalities
5. Uses anime-style emotional storytelling and visual descriptions
6. Ends with the Pokémon making a personality-based decision or reaction

Focus on the magic of the moment and the potential for connection.
Write as if this is a pivotal scene in a Pokémon anime episode.

Begin the encounter:"""

def get_enhanced_story_prompt(context: dict) -> str:
    """Build an enhanced story prompt using rich context data."""
    prompt_parts = []
    
    # Header
    prompt_parts.append("🎬 ANIME-STYLE POKÉMON STORY GENERATION")
    prompt_parts.append("=" * 50)
    prompt_parts.append("")
    
    # Instructions
    prompt_parts.append("You are creating an immersive Pokémon anime-style adventure scene.")
    prompt_parts.append("Use the following rich context to create a character-driven narrative:")
    prompt_parts.append("")
    
    # Location context
    if context.get('location_atmosphere'):
        prompt_parts.append(f"🏞️ LOCATION: {context['location_atmosphere']}")
        prompt_parts.append("")
    
    # Character personalities
    if context.get('character_personalities'):
        prompt_parts.append("👥 CHARACTERS:")
        for char in context['character_personalities']:
            prompt_parts.append(f"   • {char}")
        prompt_parts.append("")
    
    # Pokémon personalities
    if context.get('pokemon_personalities'):
        prompt_parts.append("🐾 POKÉMON:")
        for pokemon in context['pokemon_personalities']:
            prompt_parts.append(f"   • {pokemon}")
        prompt_parts.append("")
    
    # Seasonal atmosphere
    if context.get('seasonal_atmosphere'):
        prompt_parts.append(f"🌸 SEASON: {context['seasonal_atmosphere']}")
        prompt_parts.append("")
    
    # Recent events
    if context.get('recent_events'):
        prompt_parts.append("📖 RECENT EVENTS:")
        for event in context['recent_events']:
            prompt_parts.append(f"   • {event}")
        prompt_parts.append("")
    
    # Story generation instructions
    prompt_parts.append("**STORY REQUIREMENTS:**")
    prompt_parts.append("• Show character personalities through authentic dialogue and actions")
    prompt_parts.append("• Incorporate the location's unique atmosphere and details")
    prompt_parts.append("• Reflect the seasonal mood and any ongoing events")
    prompt_parts.append("• Use anime-style emotional storytelling and visual descriptions")
    prompt_parts.append("• Create meaningful interactions between characters and Pokémon")
    prompt_parts.append("• End with 2-3 choices that reflect the established personalities")
    prompt_parts.append("")
    prompt_parts.append("Write a compelling 2-3 paragraph scene that captures the magic of this moment:")
    prompt_parts.append("")
    
    return "\n".join(prompt_parts) 