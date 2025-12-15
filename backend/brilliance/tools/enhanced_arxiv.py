# enhanced_arxiv.py
"""
Enhanced arXiv search system with adjacent terminology searches and intelligent relevance filtering.
Conducts multiple searches with expanded terminology and uses AI agents to filter for relevance.
"""

from typing import List, Dict, Any, Optional, Tuple
import asyncio
import time
from dataclasses import dataclass

from .arxiv import _fetch as _fetch_arxiv_original
from .terminology_expander import expand_query_terminology, ExpandedTerminology
from .relevance_filter import filter_papers_by_relevance, RelevanceFilterResults
from .domain_classifier import DomainContext, classify_papers_by_domain, DomainClassificationResult


@dataclass
class EnhancedSearchResults:
    """Results from enhanced arXiv search."""
    original_query: str
    expanded_terminology: ExpandedTerminology
    search_queries_used: List[str]
    total_papers_found: int
    papers_after_filtering: int
    papers_after_domain_filtering: int
    relevance_filter_results: RelevanceFilterResults
    domain_filter_results: Optional[List[DomainClassificationResult]]
    final_papers_text: str
    search_metadata: Dict[str, Any]


class EnhancedArxivSearch:
    """Enhanced arXiv search with terminology expansion and relevance filtering."""
    
    def __init__(self, 
                 max_searches: int = 8,
                 max_papers_per_search: int = 25,
                 min_relevance_score: float = 0.4,
                 enable_ai_expansion: bool = True,
                 enable_relevance_filtering: bool = True,
                 enable_domain_filtering: bool = True):
        """
        Initialize enhanced arXiv search.
        
        Args:
            max_searches: Maximum number of search queries to execute
            max_papers_per_search: Maximum papers per individual search
            min_relevance_score: Minimum relevance score for filtering
            enable_ai_expansion: Whether to use AI for terminology expansion
            enable_relevance_filtering: Whether to use AI for relevance filtering
            enable_domain_filtering: Whether to use domain-based filtering
        """
        self.max_searches = max_searches
        self.max_papers_per_search = max_papers_per_search
        self.min_relevance_score = min_relevance_score
        self.enable_ai_expansion = enable_ai_expansion
        self.enable_relevance_filtering = enable_relevance_filtering
        self.enable_domain_filtering = enable_domain_filtering
    
    def _build_search_queries(self, query: str, expanded_terms: ExpandedTerminology) -> List[str]:
        """
        Build multiple search queries from original query and expanded terminology.
        
        Args:
            query: Original search query
            expanded_terms: Expanded terminology
            
        Returns:
            List of search query strings
        """
        queries = []
        
        # 1. Original query (highest priority)
        queries.append(query)
        
        # 2. Primary terms combinations
        if expanded_terms.primary_terms:
            primary_query = " ".join(expanded_terms.primary_terms[:4])
            if primary_query != query:
                queries.append(primary_query)
        
        # 3. Adjacent terms searches
        for i, term in enumerate(expanded_terms.adjacent_terms[:3]):
            if expanded_terms.primary_terms:
                adjacent_query = f"{expanded_terms.primary_terms[0]} {term}"
                queries.append(adjacent_query)
            else:
                queries.append(term)
        
        # 4. Alternative phrasing searches
        for alt_phrase in expanded_terms.alternative_phrasings[:2]:
            if len(alt_phrase) > 3:  # Avoid very short terms
                queries.append(alt_phrase)
        
        # 5. Narrower terms for more specific results
        for narrow_term in expanded_terms.narrower_terms[:2]:
            if expanded_terms.primary_terms:
                narrow_query = f"{expanded_terms.primary_terms[0]} {narrow_term}"
                queries.append(narrow_query)
        
        # 6. Related concepts
        for related in expanded_terms.related_concepts[:2]:
            if len(related) > 3:
                queries.append(related)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower and q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q.strip())
        
        return unique_queries[:self.max_searches]
    
    async def _execute_search_queries(self, search_queries: List[str]) -> Tuple[List[str], Dict[str, Any]]:
        """
        Execute multiple search queries against arXiv.
        
        Args:
            search_queries: List of search query strings
            
        Returns:
            Tuple of (paper_texts, metadata)
        """
        paper_texts = []
        metadata = {
            "queries_executed": [],
            "papers_per_query": {},
            "failed_queries": [],
            "total_execution_time": 0
        }
        
        start_time = time.time()
        
        for i, query in enumerate(search_queries):
            try:
                # Add delay between requests to respect arXiv rate limits
                if i > 0:
                    time.sleep(3)
                
                print(f"🔍 Executing search {i+1}/{len(search_queries)}: {query[:50]}...")
                
                result = _fetch_arxiv_original(query, self.max_papers_per_search)
                
                if result and result != "No papers found." and not result.startswith("Error"):
                    paper_texts.append(result)
                    metadata["queries_executed"].append(query)
                    
                    # Count papers in this result
                    paper_count = len([p for p in result.split('\n\n') if p.strip()])
                    metadata["papers_per_query"][query] = paper_count
                    
                    print(f"✓ Found {paper_count} papers for: {query[:50]}...")
                else:
                    metadata["failed_queries"].append(query)
                    print(f"✗ No results for: {query[:50]}...")
                    
            except Exception as e:
                metadata["failed_queries"].append(query)
                print(f"✗ Error searching '{query[:50]}...': {str(e)}")
                continue
        
        metadata["total_execution_time"] = time.time() - start_time
        
        return paper_texts, metadata
    
    def _deduplicate_papers(self, paper_texts: List[str]) -> str:
        """
        Deduplicate papers across multiple search results.
        
        Args:
            paper_texts: List of paper text results
            
        Returns:
            Combined and deduplicated paper text
        """
        if not paper_texts:
            return "No papers found."
        
        # Parse papers and deduplicate by title
        seen_titles = set()
        unique_papers = []
        
        for paper_text in paper_texts:
            paper_blocks = paper_text.split('\n\n')
            
            for block in paper_blocks:
                if not block.strip():
                    continue
                
                # Extract title (first line)
                lines = block.strip().split('\n')
                if not lines:
                    continue
                
                title_line = lines[0]
                
                # Clean title for comparison
                import re
                clean_title = re.sub(r'\s*\(\d{4}\).*$', '', title_line).strip().lower()
                
                if clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_papers.append(block.strip())
        
        return '\n\n'.join(unique_papers)
    
    async def enhanced_search(self, 
                            query: str, 
                            max_final_papers: Optional[int] = None,
                            domain_context: Optional[DomainContext] = None) -> EnhancedSearchResults:
        """
        Perform enhanced arXiv search with terminology expansion and relevance filtering.
        
        Args:
            query: Original research query
            max_final_papers: Maximum number of final papers to return
            domain_context: Domain filtering context (user's specialty domains)
            
        Returns:
            EnhancedSearchResults object
        """
        print(f"🚀 Starting enhanced arXiv search for: {query}")
        
        # Step 1: Expand terminology
        print("📝 Expanding terminology...")
        if domain_context:
            print(f"   Using domain context: {[d.value for d in domain_context.primary_domains]}")
        
        expanded_terms = expand_query_terminology(
            query, 
            use_ai=self.enable_ai_expansion,
            max_terms_per_category=10,
            domain_context=domain_context
        )
        
        print(f"   Primary terms: {expanded_terms.primary_terms[:3]}")
        print(f"   Adjacent terms: {expanded_terms.adjacent_terms[:3]}")
        print(f"   Alternative phrasings: {expanded_terms.alternative_phrasings[:3]}")
        
        # Step 2: Build search queries
        search_queries = self._build_search_queries(query, expanded_terms)
        print(f"🔧 Generated {len(search_queries)} search queries")
        
        # Step 3: Execute searches
        print("🔍 Executing searches...")
        paper_texts, search_metadata = await self._execute_search_queries(search_queries)
        
        # Step 4: Deduplicate papers
        print("🔄 Deduplicating papers...")
        combined_papers = self._deduplicate_papers(paper_texts)
        
        total_papers = len([p for p in combined_papers.split('\n\n') if p.strip()])
        print(f"📚 Found {total_papers} unique papers total")
        
        # Step 5: Apply domain filtering
        domain_filtered_papers = combined_papers
        domain_results = None
        
        if self.enable_domain_filtering and domain_context and combined_papers != "No papers found.":
            print("🏷️ Filtering papers by domain relevance...")
            
            domain_results = await classify_papers_by_domain(combined_papers, domain_context)
            
            if domain_results:
                # Filter papers based on domain classification
                relevant_paper_ids = {result.paper_id for result in domain_results if result.is_relevant_to_context}
                
                # Reconstruct papers text with only domain-relevant papers
                paper_blocks = combined_papers.split('\n\n')
                filtered_blocks = []
                
                for i, block in enumerate(paper_blocks):
                    if not block.strip():
                        continue
                    
                    paper_id = f"paper_{i}_{hash(block.split('\n')[0]) % 10000}"
                    if paper_id in relevant_paper_ids:
                        # Add domain classification info to the paper
                        domain_result = next((r for r in domain_results if r.paper_id == paper_id), None)
                        if domain_result:
                            domain_info = f"\n[DOMAIN: {', '.join([d.value for d in domain_result.detected_domains[:2]])} - Score: {domain_result.relevance_score:.2f}]"
                            filtered_blocks.append(block + domain_info)
                        else:
                            filtered_blocks.append(block)
                
                domain_filtered_papers = '\n\n'.join(filtered_blocks)
                print(f"🏷️ Domain filtered to {len(filtered_blocks)} papers from {len(domain_results)} classified")
                
                # Show domain exclusions
                excluded_count = len(domain_results) - len(filtered_blocks)
                if excluded_count > 0:
                    exclusion_reasons = set()
                    for result in domain_results:
                        if not result.is_relevant_to_context:
                            exclusion_reasons.update(result.exclusion_reasons[:2])  # Show top 2 reasons
                    
                    if exclusion_reasons:
                        print(f"   Excluded {excluded_count} papers: {'; '.join(list(exclusion_reasons)[:2])}")
            else:
                print("   No domain classifications available")
        
        # Step 6: Apply relevance filtering
        final_papers_text = domain_filtered_papers
        relevance_results = None
        
        if self.enable_relevance_filtering and domain_filtered_papers != "No papers found.":
            print("🎯 Filtering papers by relevance...")
            
            final_papers_text, relevance_results = await filter_papers_by_relevance(
                query=query,
                papers_text=domain_filtered_papers,
                min_relevance_score=self.min_relevance_score,
                max_papers=max_final_papers
            )
            
            print(f"✓ Filtered to {relevance_results.filtered_count} relevant papers")
            print(f"   Highly relevant: {len(relevance_results.highly_relevant)}")
            print(f"   Moderately relevant: {len(relevance_results.moderately_relevant)}")
        
        # Calculate final counts
        papers_after_domain = len([p for p in domain_filtered_papers.split('\n\n') if p.strip()]) if domain_filtered_papers != "No papers found." else 0
        papers_after_relevance = relevance_results.filtered_count if relevance_results else papers_after_domain
        
        # Create results object
        return EnhancedSearchResults(
            original_query=query,
            expanded_terminology=expanded_terms,
            search_queries_used=search_metadata["queries_executed"],
            total_papers_found=total_papers,
            papers_after_filtering=papers_after_relevance,
            papers_after_domain_filtering=papers_after_domain,
            relevance_filter_results=relevance_results,
            domain_filter_results=domain_results,
            final_papers_text=final_papers_text,
            search_metadata=search_metadata
        )


# Convenience functions
async def enhanced_arxiv_search(query: str, 
                              max_results: int = 50,
                              min_relevance_score: float = 0.4,
                              enable_ai_expansion: bool = True,
                              enable_relevance_filtering: bool = True,
                              domain_context: Optional[DomainContext] = None) -> str:
    """
    Perform enhanced arXiv search and return formatted results.
    
    Args:
        query: Research query
        max_results: Maximum number of final papers
        min_relevance_score: Minimum relevance score for filtering
        enable_ai_expansion: Whether to use AI for terminology expansion
        enable_relevance_filtering: Whether to use AI for relevance filtering
        domain_context: Domain filtering context
        
    Returns:
        Formatted paper results text
    """
    search_engine = EnhancedArxivSearch(
        max_searches=8,
        max_papers_per_search=20,
        min_relevance_score=min_relevance_score,
        enable_ai_expansion=enable_ai_expansion,
        enable_relevance_filtering=enable_relevance_filtering,
        enable_domain_filtering=domain_context is not None
    )
    
    results = await search_engine.enhanced_search(query, max_results, domain_context)
    return results.final_papers_text


def enhanced_arxiv_search_sync(query: str, 
                             max_results: int = 50,
                             min_relevance_score: float = 0.4,
                             enable_ai_expansion: bool = True,
                             enable_relevance_filtering: bool = True,
                             domain_context: Optional[DomainContext] = None) -> str:
    """
    Synchronous wrapper for enhanced arXiv search.
    
    Args:
        query: Research query
        max_results: Maximum number of final papers
        min_relevance_score: Minimum relevance score for filtering
        enable_ai_expansion: Whether to use AI for terminology expansion
        enable_relevance_filtering: Whether to use AI for relevance filtering
        domain_context: Domain filtering context
        
    Returns:
        Formatted paper results text
    """
    import asyncio
    return asyncio.run(enhanced_arxiv_search(
        query, max_results, min_relevance_score, 
        enable_ai_expansion, enable_relevance_filtering, domain_context
    ))
