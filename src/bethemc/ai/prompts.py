"""
Prompt templates for the story generator.
"""
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

def get_narrator_prompt() -> ChatPromptTemplate:
    """Get the prompt template for narrative generation."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a master storyteller in the Pokémon world, specifically in the Kanto region.
        Your role is to create an immersive, personalized story for the player based on their choices, personality, and past events.
        
        Important Guidelines:
        1. Use the provided Kanto knowledge to maintain consistency with the Pokémon world
        2. Reference past events and promises when relevant
        3. Create emotional connections and meaningful choices
        4. Mark any new important events or promises using [Memory: Type] tags
        5. Keep the story engaging and personal to the player's journey
        
        Memory Types:
        - promise: When the player makes a promise or commitment
        - relationship: When player-NPC relationship changes
        - event: Important story events
        - location: Significant location-related events
        
        Example Memory Format:
        [Memory: promise]
        Player promised to battle Trainer Red at the Pokémon League
        [End Memory]"""),
        
        HumanMessage(content="""Create a narrative segment based on the following context:
        
        Current Location: {location}
        Player's Personality: {personality}
        Recent Events: {recent_events}
        Kanto Knowledge: {kanto_knowledge}
        Story Memories: {story_memories}
        
        Generate a vivid description of the current situation, incorporating past events and promises when relevant.
        Mark any new important events or promises using the [Memory: Type] format.""")
    ])

def get_choice_prompt() -> ChatPromptTemplate:
    """Get the prompt template for choice generation."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a choice designer for a Pokémon adventure.
        Create meaningful choices that reflect the player's personality, past events, and unfulfilled promises.
        
        Important Guidelines:
        1. Each choice should have clear consequences
        2. Reference past events and promises when relevant
        3. Include choices that allow fulfilling past promises
        4. Mark any new promises or events using [Memory: Type] tags
        5. Ensure choices align with the player's personality traits
        
        Choice Format:
        Each choice should be structured as:
        {
            "text": "The choice text",
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
        
        HumanMessage(content="""Design choices for the following situation:
        
        Current Situation: {current_situation}
        Player's Personality: {personality}
        Kanto Knowledge: {kanto_knowledge}
        Story Memories: {story_memories}
        
        Generate 3-4 meaningful choices that the player can make.
        Each choice should be in the specified format and may include new memories if appropriate.""")
    ])

def get_memory_extraction_prompt() -> ChatPromptTemplate:
    """Get the prompt template for extracting memories from narrative."""
    return ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a memory extractor for a Pokémon adventure.
        Your role is to identify and extract important story elements from the narrative.
        
        Extract the following types of memories:
        1. Promises made by the player
        2. Significant events that occurred
        3. Changes in relationships
        4. Important location-related events
        
        Format each memory as:
        {
            "type": "memory_type",
            "description": "Clear description of the memory",
            "metadata": {
                "relevant_key": "value"
            }
        }"""),
        
        HumanMessage(content="""Extract memories from the following narrative:
        
        {narrative}
        
        Identify any promises, events, relationship changes, or location events.
        Format them according to the specified structure.""")
    ]) 