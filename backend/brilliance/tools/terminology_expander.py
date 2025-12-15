# terminology_expander.py
"""
Terminology expansion system for generating adjacent and related search terms.
Uses semantic similarity and domain knowledge to expand search queries.
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import re
from agents import Agent, Runner
import os


@dataclass
class ExpandedTerminology:
    """Container for expanded terminology results."""
    primary_terms: List[str]
    adjacent_terms: List[str] 
    broader_terms: List[str]
    narrower_terms: List[str]
    related_concepts: List[str]
    alternative_phrasings: List[str]


class TerminologyExpander:
    """Expands search terminology using domain knowledge and semantic relationships."""
    
    def __init__(self):
        self._domain_mappings = self._load_domain_mappings()
        self._synonym_mappings = self._load_synonym_mappings()
        
    def _load_domain_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load domain-specific terminology mappings."""
        return {
            "machine_learning": {
                "broader": ["artificial intelligence", "neural networks", "deep learning", "computer science"],
                "narrower": ["supervised learning", "unsupervised learning", "reinforcement learning", "transfer learning"],
                "adjacent": ["natural language processing", "computer vision", "robotics", "data mining"],
                "methods": ["transformer", "CNN", "RNN", "GAN", "VAE", "attention mechanism", "gradient descent"]
            },
            "nlp": {
                "broader": ["machine learning", "artificial intelligence", "computational linguistics"],
                "narrower": ["text classification", "sentiment analysis", "named entity recognition", "machine translation"],
                "adjacent": ["speech recognition", "information retrieval", "knowledge graphs", "dialogue systems"],
                "methods": ["BERT", "GPT", "T5", "word embeddings", "tokenization", "parsing"]
            },
            "computer_vision": {
                "broader": ["machine learning", "artificial intelligence", "image processing"],
                "narrower": ["object detection", "image segmentation", "face recognition", "optical character recognition"],
                "adjacent": ["robotics", "medical imaging", "autonomous vehicles", "augmented reality"],
                "methods": ["convolutional neural network", "YOLO", "R-CNN", "U-Net", "ResNet", "feature extraction"]
            },
            "biomedical": {
                "broader": ["medicine", "biology", "healthcare", "life sciences"],
                "narrower": ["drug discovery", "genomics", "proteomics", "clinical trials"],
                "adjacent": ["bioinformatics", "medical imaging", "epidemiology", "pharmacology"],
                "methods": ["GWAS", "RNA-seq", "mass spectrometry", "PCR", "immunoassay"]
            },
            "materials_science": {
                "broader": ["chemistry", "physics", "engineering"],
                "narrower": ["nanomaterials", "polymers", "ceramics", "metals", "composites"],
                "adjacent": ["chemical engineering", "mechanical engineering", "solid state physics"],
                "methods": ["synthesis", "characterization", "DFT", "molecular dynamics", "X-ray diffraction"]
            },
            "physics": {
                "broader": ["natural sciences", "physical sciences"],
                "narrower": ["quantum physics", "condensed matter", "particle physics", "astrophysics"],
                "adjacent": ["chemistry", "materials science", "engineering", "mathematics"],
                "methods": ["spectroscopy", "microscopy", "simulation", "theoretical modeling"]
            }
        }
    
    def _load_synonym_mappings(self) -> Dict[str, List[str]]:
        """Load synonym mappings for common terms."""
        return {
            "neural network": ["neural net", "artificial neural network", "ANN", "connectionist model"],
            "machine learning": ["ML", "statistical learning", "artificial intelligence", "AI"],
            "deep learning": ["deep neural network", "DNN", "deep net"],
            "natural language processing": ["NLP", "computational linguistics", "language processing"],
            "computer vision": ["CV", "machine vision", "image analysis", "visual computing"],
            "reinforcement learning": ["RL", "reward learning", "sequential decision making"],
            "transformer": ["attention model", "self-attention", "multi-head attention"],
            "convolutional neural network": ["CNN", "ConvNet", "convolutional network"],
            "recurrent neural network": ["RNN", "recurrent network", "sequential network"],
            "generative adversarial network": ["GAN", "adversarial network", "generative model"],
            "variational autoencoder": ["VAE", "variational encoder", "latent variable model"],
            "large language model": ["LLM", "foundation model", "pretrained model"],
            "few-shot learning": ["meta-learning", "learning to learn", "N-shot learning"],
            "zero-shot learning": ["zero-shot", "unseen class recognition"],
            "transfer learning": ["domain adaptation", "knowledge transfer", "fine-tuning"],
            "representation learning": ["feature learning", "embedding learning", "latent representation"],
            "graph neural network": ["GNN", "graph network", "geometric deep learning"],
            "attention mechanism": ["attention", "self-attention", "cross-attention"],
            "optimization": ["gradient descent", "backpropagation", "parameter optimization"],
            "regularization": ["dropout", "batch normalization", "weight decay"],
            "activation function": ["ReLU", "sigmoid", "tanh", "nonlinearity"],
            "loss function": ["objective function", "cost function", "error function"]
        }
    
    def _detect_domain(self, query: str) -> str:
        """Detect the primary domain of the query."""
        query_lower = query.lower()
        
        # Domain detection patterns
        domain_patterns = {
            "machine_learning": ["machine learning", "neural network", "deep learning", "AI", "artificial intelligence"],
            "nlp": ["natural language", "NLP", "text processing", "language model", "sentiment analysis"],
            "computer_vision": ["computer vision", "image processing", "object detection", "CNN", "visual"],
            "biomedical": ["biomedical", "medical", "clinical", "drug", "protein", "gene", "disease"],
            "materials_science": ["materials", "catalyst", "synthesis", "crystal", "molecular"],
            "physics": ["physics", "quantum", "particle", "condensed matter", "spectroscopy"]
        }
        
        domain_scores = {}
        for domain, patterns in domain_patterns.items():
            score = sum(1 for pattern in patterns if pattern.lower() in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return "general"
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from the query."""
        # Remove common stopwords and extract meaningful terms
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'for', 'with', 'of', 'in', 'on', 'to', 'by', 'from', 'at', 'as', 
            'is', 'are', 'be', 'being', 'into', 'that', 'this', 'these', 'those', 'using', 'use', 'based',
            'about', 'what', 'which', 'when', 'how', 'why', 'can', 'state', 'art', 'towards', 'toward',
            'new', 'novel', 'recent', 'improved', 'improving', 'paper', 'study', 'approach', 'method',
            'methods', 'framework', 'system', 'systems'
        }
        
        # Extract phrases in quotes first
        quoted_phrases = re.findall(r'"([^"]+)"', query)
        
        # Remove quoted phrases from query to avoid duplication
        query_no_quotes = re.sub(r'"[^"]+"', ' ', query)
        
        # Tokenize and filter
        tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-_]*\b', query_no_quotes.lower())
        filtered_tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        # Combine multi-word technical terms
        concepts = quoted_phrases.copy()
        
        # Look for common multi-word terms
        text = query_no_quotes.lower()
        multi_word_terms = [
            "machine learning", "deep learning", "neural network", "natural language processing",
            "computer vision", "reinforcement learning", "transfer learning", "few-shot learning",
            "zero-shot learning", "large language model", "transformer model", "attention mechanism",
            "graph neural network", "convolutional neural network", "recurrent neural network",
            "generative adversarial network", "variational autoencoder", "representation learning"
        ]
        
        for term in multi_word_terms:
            if term in text:
                concepts.append(term)
        
        # Add significant single tokens
        concepts.extend(filtered_tokens[:10])  # Limit to avoid too many terms
        
        return list(set(concepts))  # Remove duplicates
    
    def expand_terminology(self, query: str, max_terms_per_category: int = 15) -> ExpandedTerminology:
        """
        Expand terminology for the given query.
        
        Args:
            query: Original search query
            max_terms_per_category: Maximum terms to return per category
            
        Returns:
            ExpandedTerminology object with categorized expanded terms
        """
        domain = self._detect_domain(query)
        key_concepts = self._extract_key_concepts(query)
        
        primary_terms = key_concepts.copy()
        adjacent_terms = []
        broader_terms = []
        narrower_terms = []
        related_concepts = []
        alternative_phrasings = []
        
        # Domain-specific expansion
        if domain in self._domain_mappings:
            domain_data = self._domain_mappings[domain]
            
            # Add domain-specific terms based on detected concepts
            for concept in key_concepts:
                concept_lower = concept.lower()
                
                # Check if concept matches domain patterns
                if any(term in concept_lower for term in domain_data.get("methods", [])):
                    adjacent_terms.extend(domain_data.get("methods", []))
                    narrower_terms.extend(domain_data.get("narrower", []))
                
            broader_terms.extend(domain_data.get("broader", []))
            adjacent_terms.extend(domain_data.get("adjacent", []))
            narrower_terms.extend(domain_data.get("narrower", []))
        
        # Synonym expansion
        for concept in key_concepts:
            concept_lower = concept.lower()
            for term, synonyms in self._synonym_mappings.items():
                if term in concept_lower or any(syn.lower() in concept_lower for syn in synonyms):
                    alternative_phrasings.extend(synonyms)
                    related_concepts.append(term)
        
        # Add concept variations
        for concept in key_concepts:
            # Add plural/singular variations
            if concept.endswith('s') and len(concept) > 3:
                alternative_phrasings.append(concept[:-1])
            else:
                alternative_phrasings.append(concept + 's')
            
            # Add common suffixes/prefixes for technical terms
            if len(concept) > 4:
                related_concepts.extend([
                    f"{concept} based",
                    f"{concept} approach",
                    f"{concept} method",
                    f"novel {concept}",
                    f"improved {concept}"
                ])
        
        # Remove duplicates and limit results
        def dedupe_and_limit(terms: List[str], limit: int) -> List[str]:
            seen = set()
            result = []
            for term in terms:
                if term.lower() not in seen and term.lower() not in [p.lower() for p in primary_terms]:
                    seen.add(term.lower())
                    result.append(term)
                    if len(result) >= limit:
                        break
            return result
        
        return ExpandedTerminology(
            primary_terms=primary_terms[:max_terms_per_category],
            adjacent_terms=dedupe_and_limit(adjacent_terms, max_terms_per_category),
            broader_terms=dedupe_and_limit(broader_terms, max_terms_per_category // 2),
            narrower_terms=dedupe_and_limit(narrower_terms, max_terms_per_category),
            related_concepts=dedupe_and_limit(related_concepts, max_terms_per_category),
            alternative_phrasings=dedupe_and_limit(alternative_phrasings, max_terms_per_category)
        )


class AITerminologyExpander:
    """AI-powered terminology expander using language models."""
    
    def __init__(self):
        self._expansion_agent = self._build_expansion_agent()
    
    def _build_expansion_agent(self) -> Agent:
        """Build the terminology expansion agent."""
        instructions = """
You are an expert research librarian and terminology specialist. Your role is to expand search queries with related academic terminology to improve research paper discovery.

# Objective
Given a research query, generate comprehensive related terminology that would help find relevant academic papers across different databases (arXiv, PubMed, OpenAlex).

# Task
Analyze the input query and generate:
1. **Adjacent terms**: Related concepts in the same field
2. **Broader terms**: Higher-level categories that encompass the topic
3. **Narrower terms**: More specific subtopics
4. **Alternative phrasings**: Synonyms and different ways to express the same concepts
5. **Related methods**: Techniques, algorithms, or approaches commonly used
6. **Cross-disciplinary terms**: Related concepts from adjacent fields

# Guidelines
- Focus on academic and technical terminology
- Include both full terms and common abbreviations (e.g., "NLP" and "natural language processing")
- Consider different research communities that might study the same topic
- Include both theoretical and applied perspectives
- Limit each category to the most relevant 10-15 terms
- Avoid overly generic terms like "research", "study", "analysis"

# Output Format
Return a JSON object with the following structure:
{
  "adjacent_terms": ["term1", "term2", ...],
  "broader_terms": ["term1", "term2", ...],
  "narrower_terms": ["term1", "term2", ...],
  "alternative_phrasings": ["term1", "term2", ...],
  "related_methods": ["term1", "term2", ...],
  "cross_disciplinary": ["term1", "term2", ...]
}
"""
        
        return Agent(
            name="terminology_expander",
            instructions=instructions,
            model="gpt-4o",  # Use GPT-4 for better reasoning
        )
    
    async def expand_terminology_ai(self, query: str) -> Dict[str, List[str]]:
        """
        Use AI to expand terminology for the given query.
        
        Args:
            query: Original search query
            
        Returns:
            Dictionary with categorized expanded terms
        """
        try:
            result = await Runner.run(self._expansion_agent, query)
            # Parse the JSON output
            import json
            expanded_terms = json.loads(result.final_output)
            return expanded_terms
        except Exception as e:
            # Fallback to empty expansion if AI fails
            return {
                "adjacent_terms": [],
                "broader_terms": [],
                "narrower_terms": [],
                "alternative_phrasings": [],
                "related_methods": [],
                "cross_disciplinary": []
            }


# Convenience functions
def expand_query_terminology(query: str, use_ai: bool = True, max_terms_per_category: int = 15, domain_context=None) -> ExpandedTerminology:
    """
    Expand terminology for a research query.
    
    Args:
        query: Original search query
        use_ai: Whether to use AI-powered expansion (fallback to rule-based)
        max_terms_per_category: Maximum terms per category
        domain_context: Domain context for domain-specific expansion
        
    Returns:
        ExpandedTerminology object
    """
    rule_based_expander = TerminologyExpander()
    base_expansion = rule_based_expander.expand_terminology(query, max_terms_per_category)
    
    # If domain context provided, enhance with domain-specific terms
    if domain_context:
        # Add domain-specific keywords to the expansion
        domain_keywords = []
        for domain in domain_context.primary_domains:
            domain_name = domain.value
            if domain_name in rule_based_expander._domain_mappings:
                domain_data = rule_based_expander._domain_mappings[domain_name]
                domain_keywords.extend(domain_data.get("keywords", [])[:5])  # Top 5 keywords per domain
                domain_keywords.extend(domain_data.get("methods", [])[:3])   # Top 3 methods per domain
        
        # Add domain keywords to related concepts
        base_expansion.related_concepts.extend(domain_keywords[:10])  # Limit to avoid too many terms
        
        # Add focus keywords from domain context
        if domain_context.focus_keywords:
            base_expansion.primary_terms.extend(domain_context.focus_keywords)
    
    if use_ai:
        try:
            import asyncio
            ai_expander = AITerminologyExpander()
            ai_terms = asyncio.run(ai_expander.expand_terminology_ai(query))
            
            # Combine AI and rule-based results
            base_expansion.adjacent_terms.extend(ai_terms.get("adjacent_terms", []))
            base_expansion.broader_terms.extend(ai_terms.get("broader_terms", []))
            base_expansion.narrower_terms.extend(ai_terms.get("narrower_terms", []))
            base_expansion.alternative_phrasings.extend(ai_terms.get("alternative_phrasings", []))
            base_expansion.related_concepts.extend(ai_terms.get("related_methods", []))
            base_expansion.related_concepts.extend(ai_terms.get("cross_disciplinary", []))
            
            # Deduplicate
            def dedupe_list(items: List[str]) -> List[str]:
                seen = set()
                result = []
                for item in items:
                    if item.lower() not in seen:
                        seen.add(item.lower())
                        result.append(item)
                return result[:max_terms_per_category]
            
            base_expansion.adjacent_terms = dedupe_list(base_expansion.adjacent_terms)
            base_expansion.broader_terms = dedupe_list(base_expansion.broader_terms)
            base_expansion.narrower_terms = dedupe_list(base_expansion.narrower_terms)
            base_expansion.alternative_phrasings = dedupe_list(base_expansion.alternative_phrasings)
            base_expansion.related_concepts = dedupe_list(base_expansion.related_concepts)
            
        except Exception:
            # If AI expansion fails, use rule-based only
            pass
    
    return base_expansion
