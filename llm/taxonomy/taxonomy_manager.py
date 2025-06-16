import os
import logging

logger = logging.getLogger(__name__)

# 文件路径 (相对于项目根目录)
TAXONOMY_FILE_PATH = '../../docs/classification_taxonomy.md'

class TaxonomyManager:
    def __init__(self, taxonomy_file_path: str = TAXONOMY_FILE_PATH):
        self.taxonomy_file_path = taxonomy_file_path
        self.categories = []
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Loads categories from the taxonomy Markdown file."""
        # Note: This is a basic loader assuming the file contains a simple list.
        # For complex Markdown or hierarchical taxonomy, more sophisticated parsing is needed.
        full_path = os.path.join(os.path.dirname(__file__), self.taxonomy_file_path)
        if not os.path.exists(full_path):
            logger.error(f"Taxonomy file not found: {full_path}. Please create it.")
            # Or raise an error: raise FileNotFoundError(f"Taxonomy file not found: {full_path}")
            self.categories = []
            return

        logger.info(f"Loading taxonomy from {full_path}")
        self.categories = []
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Assuming each line is a category, or a Markdown list item like "- Category Name"
                    if line and not line.startswith('#'): # Skip empty lines and markdown headers
                         # Basic cleaning: remove list markers like "- "
                         if line.startswith('- '):
                              line = line[2:].strip()
                         if line:
                            self.categories.append(line)

            if not self.categories:
                 logger.warning(f"No categories loaded from {full_path}. Check file content.")
            else:
                 logger.info(f"Loaded {len(self.categories)} categories.")
                 logger.debug(f"Categories: {self.categories}")

        except Exception as e:
            logger.error(f"Error loading taxonomy file {full_path}: {e}", exc_info=True)
            self.categories = []

    def get_categories(self) -> list[str]:
        """Returns the list of loaded categories."""
        return self.categories

    def is_valid_category(self, category: str) -> bool:
        """Checks if a given category string is in the loaded taxonomy."""
        return category in self.categories

# Example usage (optional, for testing the module)
# if __name__ == "__main__":
#     # Adjust path if running directly from llm/taxonomy/
#     # manager = TaxonomyManager('classification_taxonomy.md') # Assuming it's in the same directory for testing
#     # Or use the path relative to project root
#     manager = TaxonomyManager('../../docs/classification_taxonomy.md')
#     print(f"Loaded Categories: {manager.get_categories()}")
#     print(f"Is 'Technology' a valid category? {manager.is_valid_category('Technology')}")
#     print(f"Is 'InvalidCategory' a valid category? {manager.is_valid_category('InvalidCategory')}")