# enhanced_search_config.py
"""
Configuration settings for enhanced search capabilities.
"""

import os
from typing import Dict, Any


class EnhancedSearchConfig:
    """Configuration for enhanced search features."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration settings from environment variables with defaults."""
        return {
            # Enhanced arXiv search settings
            "use_enhanced_arxiv": os.getenv("USE_ENHANCED_ARXIV", "true").lower() == "true",
            "max_searches_per_query": int(os.getenv("MAX_SEARCHES_PER_QUERY", "8")),
            "max_papers_per_search": int(os.getenv("MAX_PAPERS_PER_SEARCH", "25")),
            "min_relevance_score": float(os.getenv("MIN_RELEVANCE_SCORE", "0.4")),
            
            # Terminology expansion settings
            "enable_ai_expansion": os.getenv("ENABLE_AI_EXPANSION", "true").lower() == "true",
            "max_terms_per_category": int(os.getenv("MAX_TERMS_PER_CATEGORY", "15")),
            
            # Relevance filtering settings
            "enable_relevance_filtering": os.getenv("ENABLE_RELEVANCE_FILTERING", "true").lower() == "true",
            "relevance_model": os.getenv("RELEVANCE_MODEL", "gpt-4o"),
            
            # Search optimization settings
            "enable_search_deduplication": os.getenv("ENABLE_SEARCH_DEDUPLICATION", "true").lower() == "true",
            "search_timeout_seconds": int(os.getenv("SEARCH_TIMEOUT_SECONDS", "300")),
            
            # Output settings
            "include_relevance_scores": os.getenv("INCLUDE_RELEVANCE_SCORES", "true").lower() == "true",
            "verbose_search_logging": os.getenv("VERBOSE_SEARCH_LOGGING", "false").lower() == "true"
        }
    
    @staticmethod
    def is_enhanced_arxiv_enabled() -> bool:
        """Check if enhanced arXiv search is enabled."""
        return os.getenv("USE_ENHANCED_ARXIV", "true").lower() == "true"
    
    @staticmethod
    def get_max_final_papers() -> int:
        """Get maximum number of final papers to return."""
        return int(os.getenv("MAX_FINAL_PAPERS", "50"))
    
    @staticmethod
    def get_search_strategy() -> str:
        """Get the search strategy (enhanced, standard, or hybrid)."""
        return os.getenv("SEARCH_STRATEGY", "enhanced").lower()


# Convenience function
def get_enhanced_search_config() -> Dict[str, Any]:
    """Get enhanced search configuration."""
    return EnhancedSearchConfig.get_config()
