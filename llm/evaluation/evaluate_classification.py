import jsonlines
import os
import logging
import asyncio
from typing import Dict, Any, Optional, List

# Import modules from your project
from llm.taxonomy.taxonomy_manager import TaxonomyManager
# Assuming you created a classifier.py module in llm/inference/
from llm.inference.classifier import classify_article_with_llm # Import the LLM classification function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File paths (relative to project root)
INPUT_PROCESSED_DATA_PATH = '../../data/processed/formatted_evaluation_data.jsonl'
OUTPUT_EVALUATION_DATA_PATH = '../../data/processed/evaluation_dataset_with_labels.jsonl'

# Taxonomy Manager
# Adjust the path if necessary
taxonomy_manager = TaxonomyManager('../../docs/classification_taxonomy.md')
VALID_CATEGORIES = taxonomy_manager.get_categories()

# --- Classification Functions (Placeholders for Google API) ---
# You need to implement this based on your Google API access and documentation
async def classify_with_google_api(article_data: Dict[str, Any]) -> Optional[str]:
    """
    Classifies a single news article using Google Classification API.
    (Placeholder - IMPLEMENT THIS)
    """
    logger.debug(f"Calling Google API placeholder for {article_data.get('url', 'N/A')}...")
    # --- YOUR GOOGLE API CALL LOGIC HERE ---
    # Example: Send article_data['content'] to Google API
    # Parse response to get classification result
    # Map Google's classification to your taxonomy using map_google_to_iab.py logic
    # from scripts.data_processing.map_google_to_iab import map_google_category # Example mapping function

    # For now, return a dummy result
    await asyncio.sleep(0.1) # Simulate async work
    dummy_google_category = None # Replace with actual API call result

    # Example mapping logic (if needed)
    # if dummy_google_category:
    #      return map_google_category(dummy_google_category)
    # else:
    #      return None
    logger.warning("Google API classification is a placeholder and not implemented.")
    return None # Or return a dummy category for testing: "Technology"


# --- Evaluation and Labeling Logic ---

def determine_ground_truth_label(
    llm_category: Optional[str],
    google_category: Optional[str] # Assuming Google API provides a single category
    # Add other potential sources of labels here
) -> Optional[str]:
    """
    Determines the 'ground truth' label based on agreement between classifiers.

    Args:
        llm_category: Classification result from LLM.
        google_category: Classification result from Google API (mapped to your taxonomy).

    Returns:
        The determined ground truth label, or None if no agreement/source is available.
    """
    # --- Your Agreement Logic ---
    # This is where you define what constitutes "agreement"
    # Simple agreement: Both return the exact same valid category
    if llm_category and google_category and llm_category == google_category and taxonomy_manager.is_valid_category(llm_category):
        logger.debug(f"Agreement found: {llm_category}")
        return llm_category

    # More complex logic:
    # - What if one returns a subcategory and the other a parent?
    # - What if only one returns a result? Use that result if it's valid?
    # - What if results are close but not exact?
    # - What if you have a tie-breaking rule?

    # Example: If only LLM provides a valid category, use it.
    # This assumes LLM is reasonably reliable even without Google.
    if llm_category and taxonomy_manager.is_valid_category(llm_category):
         logger.debug(f"Using LLM result as ground truth (no Google agreement): {llm_category}")
         return llm_category

    # Example: If only Google provides a valid category (after mapping), use it.
    # if google_category and taxonomy_manager.is_valid_category(google_category):
    #      logger.debug(f"Using Google result as ground truth (no LLM agreement): {google_category}")
    #      return google_category


    logger.debug("No reliable ground truth determined from classifiers.")
    return None # No agreement or valid single source found


async def build_evaluation_dataset(input_path: str, output_path: str):
    """
    Builds the evaluation dataset by classifying articles and determining ground truth labels.
    """
    logger.info(f"Starting evaluation dataset building from {input_path}")

    total_articles = 0
    processed_articles = 0
    evaluated_items = []

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    if not os.path.exists(input_path):
        logger.error(f"Input processed data file not found: {input_path}. Please run format_dataset.py first.")
        return

    try:
        with jsonlines.open(input_path, mode='r') as reader:
            # Collect items first if needed, or process one by one
            all_articles_data = list(reader)
            total_articles = len(all_articles_data)
            logger.info(f"Loaded {total_articles} articles for evaluation.")

            # Process articles and classify
            for article_data in all_articles_data:
                 processed_articles += 1
                 url = article_data.get('url', 'N/A')
                 logger.debug(f"Processing article {processed_articles}/{total_articles}: {url}")

                 # --- Classify using LLM ---
                 llm_category = await classify_article_with_llm(article_data)
                 article_data['llm_predicted_category'] = llm_category # Add LLM result to item

                 # --- Classify using Google API (Placeholder) ---
                 google_category = await classify_with_google_api(article_data)
                 article_data['google_predicted_category'] = google_category # Add Google result to item

                 # --- Determine Ground Truth Label ---
                 ground_truth_label = determine_ground_truth_label(llm_category, google_category)
                 article_data['ground_truth_category'] = ground_truth_label # Add ground truth label

                 evaluated_items.append(article_data)

            logger.info(f"Finished processing {processed_articles} articles for evaluation.")

        # --- Save the evaluated dataset ---
        if evaluated_items:
            with jsonlines.open(output_path, mode='w') as writer:
                writer.write_all(evaluated_items)
            logger.info(f"Successfully saved {len(evaluated_items)} evaluated items to {output_path}")
        else:
            logger.warning("No items to evaluate. Output file not created.")

    except Exception as e:
        logger.error(f"An error occurred during evaluation dataset building: {e}", exc_info=True)


if __name__ == "__main__":
    # Adjust input/output paths if running this script directly from its location
    # If running from `llm/evaluation/`, adjust paths:
    # INPUT_PROCESSED_DATA_PATH = '../../data/processed/formatted_evaluation_data.jsonl'
    # OUTPUT_EVALUATION_DATA_PATH = '../../data/processed/evaluation_dataset_with_labels.jsonl'

    # Note: Running this will trigger API calls and might incur costs!
    logger.info("Starting evaluation dataset building process. This may call external APIs.")
    asyncio.run(build_evaluation_dataset(INPUT_PROCESSED_DATA_PATH, OUTPUT_EVALUATION_DATA_PATH))
    logger.info("Evaluation dataset building process finished.")