# relevance_filter.py
"""
Intelligent relevance filtering system for research papers.
Uses AI agents to evaluate paper relevance instead of simple regex matching.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import re
from agents import Agent, Runner
import json


@dataclass
class PaperRelevanceScore:
    """Container for paper relevance evaluation."""
    paper_id: str
    title: str
    relevance_score: float  # 0.0 to 1.0
    relevance_reasons: List[str]
    key_concepts_matched: List[str]
    is_relevant: bool
    confidence: float  # 0.0 to 1.0


@dataclass
class RelevanceFilterResults:
    """Results from relevance filtering."""
    original_count: int
    filtered_count: int
    papers_scored: List[PaperRelevanceScore]
    highly_relevant: List[str]  # Paper IDs
    moderately_relevant: List[str]  # Paper IDs
    low_relevant: List[str]  # Paper IDs


class RelevanceFilter:
    """Intelligent relevance filtering for research papers."""
    
    def __init__(self):
        self._relevance_agent = self._build_relevance_agent()
    
    def _build_relevance_agent(self) -> Agent:
        """Build the relevance evaluation agent."""
        instructions = """
You are an expert research paper relevance evaluator. Your role is to assess how relevant research papers are to a given query.

# Objective
Evaluate the relevance of research papers to a specific research question or topic. You will be given:
1. The original research query/question
2. Paper titles, abstracts, and metadata

# Evaluation Criteria
Assess relevance based on:
1. **Direct topic match**: How directly does the paper address the query topic?
2. **Methodological relevance**: Does the paper use relevant methods/approaches?
3. **Conceptual overlap**: How much conceptual overlap exists between query and paper?
4. **Practical applicability**: Could findings be applied to the query domain?
5. **Novelty and impact**: Is this a significant contribution to the field?

# Scoring Scale
- **0.9-1.0**: Highly relevant - directly addresses the query, perfect match
- **0.7-0.8**: Very relevant - strong connection, most concepts align
- **0.5-0.6**: Moderately relevant - some connection, partial concept overlap
- **0.3-0.4**: Somewhat relevant - tangential connection, limited overlap
- **0.1-0.2**: Low relevance - weak connection, minimal overlap
- **0.0**: Not relevant - no meaningful connection

# Decision Threshold
- **Highly relevant**: Score ≥ 0.7 (definitely include)
- **Moderately relevant**: Score 0.4-0.69 (include if space allows)
- **Low relevant**: Score < 0.4 (exclude unless very few papers found)

# Output Format
For each paper, return a JSON object:
{
  "paper_id": "unique_identifier_or_title",
  "relevance_score": 0.85,
  "relevance_reasons": [
    "Directly addresses query topic",
    "Uses relevant methodology",
    "High-impact journal"
  ],
  "key_concepts_matched": ["concept1", "concept2"],
  "is_relevant": true,
  "confidence": 0.9
}

# Guidelines
- Be precise in scoring - avoid clustering around 0.5
- Provide specific, actionable reasons for relevance scores
- Consider both theoretical and practical relevance
- Account for recency when relevant
- Be conservative with high scores (0.9+) - reserve for exceptional matches
"""
        
        return Agent(
            name="relevance_evaluator",
            instructions=instructions,
            model="gpt-4o",
        )
    
    def _parse_papers_from_text(self, papers_text: str) -> List[Dict[str, str]]:
        """Parse paper information from text format."""
        papers = []
        
        # Split by double newlines to separate papers
        paper_blocks = papers_text.split('\n\n')
        
        for i, block in enumerate(paper_blocks):
            if not block.strip():
                continue
                
            # Extract title (first line)
            lines = block.strip().split('\n')
            if not lines:
                continue
                
            title_line = lines[0]
            
            # Extract year from title line if present (pattern: "Title (YEAR)")
            year_match = re.search(r'\((\d{4})\)', title_line)
            year = year_match.group(1) if year_match else "Unknown"
            
            # Clean title by removing year and author info
            title = re.sub(r'\s*\(\d{4}\).*$', '', title_line).strip()
            
            # Extract abstract
            abstract = ""
            authors = ""
            url = ""
            pdf = ""
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("Abstract:"):
                    abstract = line[9:].strip()
                elif line.startswith("by "):
                    authors = line[3:].strip()
                elif line.startswith("URL:"):
                    url = line[4:].strip()
                elif line.startswith("PDF:"):
                    pdf = line[4:].strip()
                elif "Abstract:" not in line and not line.startswith(("by ", "URL:", "PDF:")):
                    # Continuation of abstract
                    if abstract:
                        abstract += " " + line
                    elif not authors and not url and not pdf:
                        # Might be part of title or abstract
                        if len(line) > 50:  # Likely abstract
                            abstract = line
            
            paper_id = f"paper_{i}_{hash(title) % 10000}"
            
            papers.append({
                "paper_id": paper_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "url": url,
                "pdf": pdf
            })
        
        return papers
    
    async def evaluate_paper_relevance(
        self, 
        query: str, 
        paper: Dict[str, str]
    ) -> PaperRelevanceScore:
        """
        Evaluate relevance of a single paper to the query.
        
        Args:
            query: Original research query
            paper: Paper metadata dictionary
            
        Returns:
            PaperRelevanceScore object
        """
        # Prepare evaluation prompt
        evaluation_prompt = f"""
Research Query: {query}

Paper Information:
Title: {paper.get('title', 'N/A')}
Abstract: {paper.get('abstract', 'N/A')}
Authors: {paper.get('authors', 'N/A')}
Year: {paper.get('year', 'N/A')}

Please evaluate the relevance of this paper to the research query and return your assessment in the specified JSON format.
"""
        
        try:
            result = await Runner.run(self._relevance_agent, evaluation_prompt)
            evaluation = json.loads(result.final_output)
            
            return PaperRelevanceScore(
                paper_id=evaluation.get("paper_id", paper.get("paper_id", "unknown")),
                title=paper.get("title", ""),
                relevance_score=float(evaluation.get("relevance_score", 0.0)),
                relevance_reasons=evaluation.get("relevance_reasons", []),
                key_concepts_matched=evaluation.get("key_concepts_matched", []),
                is_relevant=bool(evaluation.get("is_relevant", False)),
                confidence=float(evaluation.get("confidence", 0.0))
            )
            
        except Exception as e:
            # Fallback scoring if AI fails
            return self._fallback_relevance_scoring(query, paper)
    
    def _fallback_relevance_scoring(self, query: str, paper: Dict[str, str]) -> PaperRelevanceScore:
        """Fallback relevance scoring using keyword matching."""
        query_lower = query.lower()
        title_lower = paper.get('title', '').lower()
        abstract_lower = paper.get('abstract', '').lower()
        
        # Extract key terms from query
        query_terms = set(re.findall(r'\b[a-zA-Z]{3,}\b', query_lower))
        
        # Count matches in title and abstract
        title_matches = sum(1 for term in query_terms if term in title_lower)
        abstract_matches = sum(1 for term in query_terms if term in abstract_lower)
        
        # Calculate basic relevance score
        total_terms = len(query_terms)
        if total_terms == 0:
            relevance_score = 0.0
        else:
            title_weight = 0.7
            abstract_weight = 0.3
            relevance_score = min(1.0, (
                title_weight * (title_matches / total_terms) +
                abstract_weight * (abstract_matches / total_terms)
            ))
        
        matched_terms = [term for term in query_terms 
                        if term in title_lower or term in abstract_lower]
        
        is_relevant = relevance_score >= 0.4
        
        return PaperRelevanceScore(
            paper_id=paper.get("paper_id", "unknown"),
            title=paper.get("title", ""),
            relevance_score=relevance_score,
            relevance_reasons=[f"Keyword matching: {len(matched_terms)}/{total_terms} terms matched"],
            key_concepts_matched=matched_terms,
            is_relevant=is_relevant,
            confidence=0.6  # Lower confidence for fallback method
        )
    
    async def filter_papers_by_relevance(
        self, 
        query: str, 
        papers_text: str,
        min_relevance_score: float = 0.4,
        max_papers: Optional[int] = None
    ) -> RelevanceFilterResults:
        """
        Filter papers by relevance to the query.
        
        Args:
            query: Original research query
            papers_text: Raw paper text from search results
            min_relevance_score: Minimum relevance score to include
            max_papers: Maximum number of papers to return (None for no limit)
            
        Returns:
            RelevanceFilterResults object
        """
        papers = self._parse_papers_from_text(papers_text)
        original_count = len(papers)
        
        if original_count == 0:
            return RelevanceFilterResults(
                original_count=0,
                filtered_count=0,
                papers_scored=[],
                highly_relevant=[],
                moderately_relevant=[],
                low_relevant=[]
            )
        
        # Evaluate each paper
        scored_papers = []
        for paper in papers:
            score = await self.evaluate_paper_relevance(query, paper)
            scored_papers.append(score)
        
        # Sort by relevance score (highest first)
        scored_papers.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Filter by minimum relevance score
        relevant_papers = [p for p in scored_papers if p.relevance_score >= min_relevance_score]
        
        # Apply max papers limit if specified
        if max_papers and len(relevant_papers) > max_papers:
            relevant_papers = relevant_papers[:max_papers]
        
        # Categorize by relevance level
        highly_relevant = [p.paper_id for p in relevant_papers if p.relevance_score >= 0.7]
        moderately_relevant = [p.paper_id for p in relevant_papers if 0.4 <= p.relevance_score < 0.7]
        low_relevant = [p.paper_id for p in relevant_papers if p.relevance_score < 0.4]
        
        return RelevanceFilterResults(
            original_count=original_count,
            filtered_count=len(relevant_papers),
            papers_scored=relevant_papers,
            highly_relevant=highly_relevant,
            moderately_relevant=moderately_relevant,
            low_relevant=low_relevant
        )
    
    def format_filtered_papers(self, papers_text: str, filter_results: RelevanceFilterResults) -> str:
        """
        Format filtered papers back to text format with relevance information.
        
        Args:
            papers_text: Original papers text
            filter_results: Results from relevance filtering
            
        Returns:
            Formatted text with only relevant papers
        """
        if not filter_results.papers_scored:
            return "No relevant papers found."
        
        papers = self._parse_papers_from_text(papers_text)
        paper_lookup = {p["paper_id"]: p for p in papers}
        
        formatted_parts = []
        
        for scored_paper in filter_results.papers_scored:
            paper = paper_lookup.get(scored_paper.paper_id)
            if not paper:
                continue
            
            relevance_indicator = ""
            if scored_paper.relevance_score >= 0.9:
                relevance_indicator = "🎯 HIGHLY RELEVANT"
            elif scored_paper.relevance_score >= 0.7:
                relevance_indicator = "⭐ VERY RELEVANT"
            elif scored_paper.relevance_score >= 0.5:
                relevance_indicator = "✓ RELEVANT"
            else:
                relevance_indicator = "~ SOMEWHAT RELEVANT"
            
            part = f"{paper['title']}"
            if paper['year'] != "Unknown":
                part += f" ({paper['year']})"
            if paper['authors']:
                part += f" by {paper['authors']}"
            
            part += f"\n[{relevance_indicator} - Score: {scored_paper.relevance_score:.2f}]"
            
            if scored_paper.relevance_reasons:
                part += f"\nRelevance: {'; '.join(scored_paper.relevance_reasons[:2])}"
            
            if paper['abstract']:
                part += f"\nAbstract: {paper['abstract']}"
            
            if paper['url']:
                part += f"\nURL: {paper['url']}"
            
            if paper['pdf']:
                part += f"\nPDF: {paper['pdf']}"
            
            formatted_parts.append(part)
        
        return "\n\n".join(formatted_parts)


# Convenience functions
async def filter_papers_by_relevance(
    query: str, 
    papers_text: str,
    min_relevance_score: float = 0.4,
    max_papers: Optional[int] = None
) -> Tuple[str, RelevanceFilterResults]:
    """
    Filter papers by relevance and return formatted results.
    
    Args:
        query: Original research query
        papers_text: Raw paper text from search results
        min_relevance_score: Minimum relevance score to include
        max_papers: Maximum number of papers to return
        
    Returns:
        Tuple of (formatted_papers_text, filter_results)
    """
    filter_system = RelevanceFilter()
    filter_results = await filter_system.filter_papers_by_relevance(
        query, papers_text, min_relevance_score, max_papers
    )
    
    formatted_text = filter_system.format_filtered_papers(papers_text, filter_results)
    
    return formatted_text, filter_results
