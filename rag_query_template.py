import random

# Define templates for different categories
sentence_templates = {
    "general": [
        "What are the most recent agricultural developments in Punjab?",
        "How has agriculture evolved in recent years, and what are its current trends?",
        "What are the challenges and opportunities in agriculture in Punjab?",
        "How do environmental conditions impact overall agricultural productivity?",
        "What are the current market trends of crops?"
    ],
    "crop_management": [
        "What are the most suitable crops to plant in the current season?",
        "What recent advancements have been made to improve crop yields?",
        "What influences the choice of crops for farmers in different regions?",
        "What are the best practices for farmers to maximize crop production?"
    ],
    "soil_health": [
        "How can farming practices be improved to enhance soil health and agricultural productivity?",
        "What are the latest techniques for managing soil fields effectively?",
        "What factors have an impact on long-term soil fertility?",
        "How have recent innovations in agriculture affected soil management strategies?"
    ],
    "irrigation": [
        "What are the most efficient irrigation methods for optimizing soil health?",
        "What factors impact water usage in agriculture?",
        "What are the latest technologies that conserve water while maintaining crop yield?",
        "What are the challenges and solutions associated with irrigation in different climates?"
    ],
    "pest_control": [
        "What are the most effective strategies for pest control in agriculture?",
        "How has the effectiveness of pesticides evolved with changing pest resistance patterns?",
        "What are the recent innovations in pesticides that reduce environmental impact?",
        "How do different pest control methods compare in terms of cost and efficacy?"
    ],
    # Add other categories similarly...
}

# Keyword to category mapping
keyword_to_category = {
    "crop": "crop_management",
    "yield": "crop_management",
    "fertilizer": "soil_health",
    "field": "soil_health",
    "irrigation": "irrigation",
    "water": "irrigation",
    "pesticides": "pest_control",
    "insect": "pest_control",
    "insects": "pest_control"
    # Add more keywords to categories as needed...
}

def extract_agricultural_keywords(sentence):
    """Extracts relevant keywords from the sentence."""
    extracted_keywords = []
    for keyword in keyword_to_category.keys():
        if keyword in sentence.lower():
            extracted_keywords.append(keyword)
    return extracted_keywords

def generate_rag_query(keyword):
    """Generates a standalone, detailed query for the RAG system."""
    category = keyword_to_category.get(keyword, "general")
    templates = sentence_templates.get(category, sentence_templates["general"])
    template = random.choice(templates)
    return template.replace("**[KEYWORD]**", keyword)

def process_sentence_for_rag(sentence):
    """Process the sentence, extract keywords, and generate RAG queries."""
    keywords = extract_agricultural_keywords(sentence)
    
    # If no keywords are found, generate a general query
    if not keywords:
        keywords = ["general"]
    
    rag_queries = [generate_rag_query(keyword) for keyword in keywords]
    return rag_queries

def get_rag_query(user_prompt):
    rag_queries = process_sentence_for_rag(user_prompt)
    print("User Prompt:", user_prompt)
    print("Generated RAG Queries:")
    for query in rag_queries:
        print(query)
        return query

# Output these queries to the RAG system and retrieve additional information
# The retrieved information, along with the original prompt, will then be passed to the LLM for final processing.
