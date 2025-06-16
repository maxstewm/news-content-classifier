import jsonlines
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 文件路径 (相对于项目根目录)
# 输入文件：爬虫输出的原始数据
# 假设你的爬虫输出到 data/extracted/evaluation_data_final.jsonl
INPUT_DATA_PATH = '../../data/extracted/evaluation_data_npr.jsonl'
# 输出文件：处理后的干净数据
OUTPUT_DATA_PATH = '../../data/processed/formatted_evaluation_data.jsonl'
#OUTPUT_DATA_PATH = './formatted_evaluation_data.jsonl'


# 过滤规则
MIN_CORE_TEXT_LENGTH = 200 # 要求提取的核心文本至少有200个字符

def format_and_filter_data(input_path: str, output_path: str):
    """
    Reads raw crawled data, filters items based on criteria,
    and formats the data for classification.
    """
    logger.info(f"Starting data formatting and filtering from {input_path}")

    processed_count = 0
    filtered_count = 0
    valid_items = []

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)  # 修改此处，添加 exist_ok=True
        logger.info(f"Created output directory: {output_dir}")

    try:
        with jsonlines.open(input_path, mode='r') as reader:
            for item in reader:
                processed_count += 1
                url = item.get('url', 'N/A')

                # --- Apply Filtering Criteria ---
                # 1. Require non-empty extracted_core_text
                core_text = item.get('extracted_core_text')
                if not core_text or len(core_text.strip()) < MIN_CORE_TEXT_LENGTH:
                    logger.debug(f"Filtering out item {url}: Core text too short or empty (Length: {len(core_text.strip()) if core_text else 0})")
                    filtered_count += 1
                    continue

                # 2. (Optional) Filter out items without a title or description if needed
                # if not item.get('title') or not item.get('description'):
                #     logger.debug(f"Filtering out item {url}: Missing title or description")
                #     filtered_count += 1
                #     continue

                # --- Format or Select Relevant Fields ---
                # Create a new dictionary with only the fields needed for classification
                # and rename/clean them if necessary.
                formatted_item = {
                    'url': url,
                    'title': item.get('title', ''),
                    # Use the potentially improved description from pipeline if available, fallback to meta
                    'description': item.get('description', ''),
                    'content': core_text.strip(), # Use the extracted core text
                    # Include other useful extracted fields for context if needed by classifier or LLM
                    'published_date': item.get('published_date'),
                    'author': item.get('author'),
                    'categories_extracted': item.get('categories'), # Keep original extracted categories
                    'tags_extracted': item.get('tags'), # Keep original extracted tags
                    # You might include rendered_html here if your classifier needs the full HTML
                    # 'rendered_html': item.get('rendered_html')
                }

                valid_items.append(formatted_item)

        logger.info(f"Finished reading and filtering. Total items processed: {processed_count}, Filtered items: {filtered_count}, Valid items: {len(valid_items)}")

        # --- Save the filtered/formatted data ---
        if valid_items:
            with jsonlines.open(output_path, mode='w') as writer:
                writer.write_all(valid_items)
            logger.info(f"Successfully saved {len(valid_items)} valid items to {output_path}")
        else:
            logger.warning("No valid items found after filtering. Output file not created.")

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}. Please ensure the crawler has run and generated data.")
    except Exception as e:
        logger.error(f"An error occurred during data processing: {e}", exc_info=True)


if __name__ == "__main__":
    # Adjust input/output paths if running this script directly from its location
    # It's usually better to run from the project root using `python scripts/data_processing/format_dataset.py`
    # If running from `scripts/data_processing/`, adjust paths:
    # INPUT_DATA_PATH = '../../data/extracted/evaluation_data_final.jsonl'
    # OUTPUT_DATA_PATH = '../../data/processed/formatted_evaluation_data.jsonl'

    format_and_filter_data(INPUT_DATA_PATH, OUTPUT_DATA_PATH)