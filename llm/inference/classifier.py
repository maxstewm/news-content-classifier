import os
import requests
import json
import logging
from typing import Optional, List, Dict, Any
# Assuming your taxonomy manager is correctly implemented
from llm.taxonomy.taxonomy_manager import TaxonomyManager

logger = logging.getLogger(__name__)

# --- LLM API Configuration (Replace with your actual API details) ---
# It's highly recommended to use environment variables for API keys!
# Example using environment variables:
LLM_API_URL = os.environ.get("LLM_API_URL", "YOUR_DEFAULT_LLM_API_URL") # e.g., "https://api.openai.com/v1/chat/completions"
LLM_API_KEY = os.environ.get("LLM_API_KEY", "YOUR_DEFAULT_LLM_API_KEY") # Your API key

# --- Taxonomy Manager ---
# Initialize TaxonomyManager to get the list of valid categories
# Adjust the path if necessary
taxonomy_manager = TaxonomyManager('../../docs/classification_taxonomy.md')
VALID_CATEGORIES = taxonomy_manager.get_categories()

# --- Prompt Template for LLM Classification ---
# This is a critical part - you need to design a good prompt!
# The prompt should instruct the LLM to classify the article based on the provided taxonomy.
# Example Prompt (adjust for the specific LLM and desired output format)
CLASSIFICATION_PROMPT_TEMPLATE = """
You are an expert news article classifier.
Your task is to read the following article and assign ONE primary category from the provided list.
Only output the category name, nothing else.
If the article does not clearly fit into any of the categories, output "Other".

Available Categories: {categories}

Article Title: {title}
Article Description: {description}
Article Content:
{content}

Primary Category:
"""

async def classify_article_with_llm(article_data: Dict[str, Any]) -> Optional[str]:
    """
    Classifies a single news article using a large language model API.

    Args:
        article_data: A dictionary containing article information (must have 'title', 'description', 'content').

    Returns:
        The predicted primary category as a string, or None if classification fails.
    """
    if not LLM_API_URL or not LLM_API_KEY:
        logger.error("LLM_API_URL or LLM_API_KEY not configured. Cannot classify.")
        return None

    if not VALID_CATEGORIES:
         logger.warning("No valid categories loaded from taxonomy. Cannot classify.")
         return None

    title = article_data.get('title', '')
    description = article_data.get('description', '')
    content = article_data.get('content', '')
    url = article_data.get('url', 'N/A')

    if not content:
        logger.warning(f"Article content is empty for {url}. Skipping classification.")
        return None

    # Format the prompt using article data and the available categories
    prompt_text = CLASSIFICATION_PROMPT_TEMPLATE.format(
        categories=", ".join(VALID_CATEGORIES),
        title=title,
        description=description,
        content=content # You might want to truncate content for long articles
    )

    # --- Make API Call to LLM (Replace with actual API client code) ---
    # This is a placeholder using requests. You'll need to adapt this
    # for the specific LLM API you are using (e.g., OpenAI Python client, Google Generative AI client).
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Example payload for a generic chat completion API
    payload = {
        "model": "YOUR_LLM_MODEL_NAME", # e.g., "gpt-4o", "gemini-pro"
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 50, # Limit response length
        "temperature": 0, # Get deterministic results
        # Add other parameters required by your API
    }

    try:
        logger.debug(f"Calling LLM API for {url}...")
        response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=60) # Add a timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse the API response (Highly dependent on API)
        response_json = response.json()
        logger.debug(f"LLM API response for {url}: {response_json}")

        # Extract the classification result from the response
        # This part is specific to the API response format
        predicted_category = None
        # Example for OpenAI chat completion:
        if 'choices' in response_json and response_json['choices']:
            # The category should be in the content of the first message
            predicted_category_raw = response_json['choices'][0].get('message', {}).get('content', '').strip()
            # Clean up the raw output (e.g., remove quotes, leading/trailing spaces)
            predicted_category = predicted_category_raw.replace('"', '').replace("'", "").strip()

        # Validate the predicted category against the taxonomy
        if predicted_category and taxonomy_manager.is_valid_category(predicted_category):
            logger.debug(f"Successfully classified {url} as: {predicted_category}")
            return predicted_category
        elif predicted_category == "Other": # Handle the "Other" category specifically if allowed
             logger.debug(f"Successfully classified {url} as: Other")
             return "Other"
        else:
            logger.warning(f"LLM returned invalid category '{predicted_category}' for {url}. Prompt:\n{prompt_text}\nResponse:\n{response_json}")
            return None # Return None for invalid or unclassifiable results

    except requests.exceptions.Timeout:
        logger.error(f"LLM API request timed out for {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling LLM API for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing LLM API response for {url}: {e}", exc_info=True)
        return None

# Example usage (optional, for testing the module)
# async def main_test():
#     test_article = {
#         'url': 'http://example.com/test-article',
#         'title': 'Testing LLM Classification',
#         'description': 'This is a test description about technology.',
#         'content': 'This article talks about the latest advancements in artificial intelligence and machine learning.'
#     }
#     category = await classify_article_with_llm(test_article)
#     print(f"Test article classified as: {category}")

# if __name__ == "__main__":
#     import asyncio
#     # Set your actual API URL and Key in environment variables or replace placeholders
#     # os.environ["LLM_API_URL"] = "..."
#     # os.environ["LLM_API_KEY"] = "..."
#     # os.environ["YOUR_LLM_MODEL_NAME"] = "..." # If needed in payload
#
#     asyncio.run(main_test())