# domain_classifier.py
"""
Domain classification and filtering system for research papers.
Provides domain-specific search guidance and paper filtering.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from agents import Agent, Runner


class ResearchDomain(Enum):
    """Research domain categories."""
    PHYSICS = "physics"
    ENGINEERING = "engineering"
    COMPUTER_SCIENCE = "computer_science"
    MATHEMATICS = "mathematics"
    CHEMISTRY = "chemistry"
    MATERIALS_SCIENCE = "materials_science"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    NEUROSCIENCE = "neuroscience"
    PSYCHOLOGY = "psychology"
    ECONOMICS = "economics"
    ENVIRONMENTAL_SCIENCE = "environmental_science"
    ASTRONOMY = "astronomy"
    GEOSCIENCES = "geosciences"
    STATISTICS = "statistics"
    
    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names for domains."""
        return {
            cls.PHYSICS.value: "Physics",
            cls.ENGINEERING.value: "Engineering",
            cls.COMPUTER_SCIENCE.value: "Computer Science",
            cls.MATHEMATICS.value: "Mathematics",
            cls.CHEMISTRY.value: "Chemistry",
            cls.MATERIALS_SCIENCE.value: "Materials Science",
            cls.BIOLOGY.value: "Biology",
            cls.MEDICINE.value: "Medicine",
            cls.NEUROSCIENCE.value: "Neuroscience",
            cls.PSYCHOLOGY.value: "Psychology",
            cls.ECONOMICS.value: "Economics",
            cls.ENVIRONMENTAL_SCIENCE.value: "Environmental Science",
            cls.ASTRONOMY.value: "Astronomy",
            cls.GEOSCIENCES.value: "Geosciences",
            cls.STATISTICS.value: "Statistics"
        }


@dataclass
class DomainContext:
    """Context information for domain-specific searches."""
    primary_domains: List[ResearchDomain]
    exclude_domains: List[ResearchDomain]
    domain_weights: Dict[ResearchDomain, float]  # 0.0 to 1.0
    focus_keywords: List[str]
    exclude_keywords: List[str]


@dataclass
class DomainClassificationResult:
    """Result of domain classification for a paper."""
    paper_id: str
    detected_domains: List[ResearchDomain]
    domain_scores: Dict[ResearchDomain, float]
    is_relevant_to_context: bool
    relevance_score: float
    exclusion_reasons: List[str]


class DomainClassifier:
    """Classifies papers by research domain and filters based on domain context."""
    
    def __init__(self):
        self._domain_patterns = self._load_domain_patterns()
        self._exclusion_patterns = self._load_exclusion_patterns()
        self._arxiv_categories = self._load_arxiv_categories()
        self._classification_agent = self._build_classification_agent()
    
    def _load_domain_patterns(self) -> Dict[ResearchDomain, Dict[str, List[str]]]:
        """Load domain-specific keyword patterns."""
        return {
            ResearchDomain.PHYSICS: {
                "keywords": [
                    "quantum", "particle", "wave", "field theory", "relativity", "thermodynamics",
                    "electromagnetism", "optics", "mechanics", "condensed matter", "plasma",
                    "photon", "electron", "proton", "neutron", "bosons", "fermions",
                    "superconductivity", "magnetism", "spectroscopy", "crystallography"
                ],
                "methods": [
                    "monte carlo simulation", "density functional theory", "molecular dynamics",
                    "finite element", "spectroscopy", "diffraction", "scattering"
                ],
                "applications": [
                    "semiconductor", "laser", "detector", "accelerator", "telescope",
                    "interferometer", "spectrometer"
                ]
            },
            ResearchDomain.ENGINEERING: {
                "keywords": [
                    "design", "optimization", "control", "system", "manufacturing", "materials",
                    "structural", "mechanical", "electrical", "chemical", "civil", "aerospace",
                    "automotive", "robotics", "automation", "sensors", "actuators",
                    "fluid dynamics", "heat transfer", "vibration", "stress", "strain",
                    "fatigue", "fracture", "composite", "alloy", "coating"
                ],
                "methods": [
                    "finite element analysis", "computational fluid dynamics", "optimization",
                    "control theory", "signal processing", "image processing", "CAD", "CAM"
                ],
                "applications": [
                    "aircraft", "spacecraft", "vehicle", "engine", "turbine", "pump",
                    "compressor", "heat exchanger", "reactor", "bridge", "building"
                ]
            },
            ResearchDomain.COMPUTER_SCIENCE: {
                "keywords": [
                    "algorithm", "data structure", "programming", "software", "hardware",
                    "artificial intelligence", "machine learning", "deep learning",
                    "neural network", "computer vision", "natural language processing",
                    "database", "network", "security", "cryptography", "blockchain",
                    "distributed systems", "cloud computing", "parallel computing"
                ],
                "methods": [
                    "supervised learning", "unsupervised learning", "reinforcement learning",
                    "gradient descent", "backpropagation", "convolutional neural network",
                    "recurrent neural network", "transformer", "attention mechanism"
                ],
                "applications": [
                    "web application", "mobile app", "game", "recommendation system",
                    "search engine", "chatbot", "autonomous vehicle", "smart city"
                ]
            },
            ResearchDomain.MATHEMATICS: {
                "keywords": [
                    "theorem", "proof", "algebra", "geometry", "calculus", "topology",
                    "analysis", "number theory", "combinatorics", "graph theory",
                    "probability", "statistics", "optimization", "differential equation",
                    "linear algebra", "abstract algebra", "real analysis", "complex analysis"
                ],
                "methods": [
                    "mathematical proof", "numerical analysis", "statistical analysis",
                    "monte carlo method", "optimization algorithm", "approximation theory"
                ],
                "applications": [
                    "cryptography", "coding theory", "mathematical modeling",
                    "financial mathematics", "actuarial science"
                ]
            },
            ResearchDomain.CHEMISTRY: {
                "keywords": [
                    "molecule", "atom", "bond", "reaction", "catalyst", "synthesis",
                    "organic", "inorganic", "physical", "analytical", "biochemistry",
                    "polymer", "crystal", "solution", "acid", "base", "oxidation",
                    "reduction", "kinetics", "thermodynamics", "spectroscopy"
                ],
                "methods": [
                    "NMR", "mass spectrometry", "chromatography", "crystallography",
                    "computational chemistry", "quantum chemistry", "molecular dynamics"
                ],
                "applications": [
                    "drug discovery", "materials synthesis", "catalysis", "battery",
                    "solar cell", "pharmaceutical", "cosmetics", "food chemistry"
                ]
            },
            ResearchDomain.MATERIALS_SCIENCE: {
                "keywords": [
                    "material", "crystal", "alloy", "composite", "polymer", "ceramic",
                    "metal", "semiconductor", "nanomaterial", "thin film", "coating",
                    "properties", "structure", "characterization", "synthesis",
                    "mechanical properties", "electrical properties", "thermal properties"
                ],
                "methods": [
                    "X-ray diffraction", "electron microscopy", "atomic force microscopy",
                    "spectroscopy", "thermal analysis", "mechanical testing"
                ],
                "applications": [
                    "electronics", "aerospace", "automotive", "energy storage",
                    "solar cells", "sensors", "biomedical implants"
                ]
            },
            ResearchDomain.BIOLOGY: {
                "keywords": [
                    "cell", "gene", "protein", "DNA", "RNA", "enzyme", "metabolism",
                    "evolution", "ecology", "organism", "species", "population",
                    "molecular biology", "cell biology", "genetics", "genomics",
                    "proteomics", "bioinformatics", "phylogeny", "biodiversity"
                ],
                "methods": [
                    "PCR", "sequencing", "cloning", "microscopy", "cell culture",
                    "immunoassay", "western blot", "flow cytometry", "CRISPR"
                ],
                "applications": [
                    "biotechnology", "genetic engineering", "conservation",
                    "agriculture", "environmental monitoring", "bioremediation"
                ]
            },
            ResearchDomain.MEDICINE: {
                "keywords": [
                    "patient", "disease", "treatment", "therapy", "drug", "clinical",
                    "diagnosis", "symptom", "pathology", "pharmacology", "epidemiology",
                    "public health", "medical imaging", "surgery", "oncology",
                    "cardiology", "neurology", "psychiatry", "pediatrics", "geriatrics"
                ],
                "methods": [
                    "clinical trial", "randomized controlled trial", "case study",
                    "meta-analysis", "systematic review", "diagnostic imaging",
                    "laboratory test", "biopsy", "genetic testing"
                ],
                "applications": [
                    "drug development", "medical device", "diagnostic tool",
                    "surgical procedure", "rehabilitation", "preventive medicine"
                ]
            },
            ResearchDomain.ASTRONOMY: {
                "keywords": [
                    "star", "galaxy", "planet", "cosmic", "universe", "telescope",
                    "observation", "astrophysics", "cosmology", "dark matter",
                    "dark energy", "black hole", "neutron star", "supernova",
                    "exoplanet", "solar system", "interstellar", "intergalactic"
                ],
                "methods": [
                    "photometry", "spectroscopy", "interferometry", "radio astronomy",
                    "space mission", "ground-based observation", "numerical simulation"
                ],
                "applications": [
                    "space exploration", "satellite", "space telescope",
                    "planetary science", "astrobiology", "navigation"
                ]
            }
        }
    
    def _load_exclusion_patterns(self) -> Dict[ResearchDomain, List[str]]:
        """Load patterns that indicate a paper should be excluded from a domain."""
        return {
            ResearchDomain.ENGINEERING: [
                # Exclude pure theoretical physics without engineering application
                "theoretical physics", "particle physics", "cosmology", "astrophysics",
                "pure mathematics", "number theory", "abstract algebra",
                # Exclude pure biology/medicine without engineering aspect
                "clinical study", "patient cohort", "epidemiological study",
                "pure biology", "ecology", "evolutionary biology"
            ],
            ResearchDomain.PHYSICS: [
                # Exclude applied engineering without physics theory
                "manufacturing process", "industrial application", "commercial product",
                "business model", "market analysis", "economic impact",
                # Exclude pure computer science
                "software engineering", "web development", "database design",
                "user interface", "mobile application"
            ],
            ResearchDomain.COMPUTER_SCIENCE: [
                # Exclude hardware engineering without CS theory
                "circuit design", "semiconductor manufacturing", "material properties",
                # Exclude pure mathematics without computational aspect
                "pure mathematics", "theoretical proof", "abstract algebra"
            ]
        }
    
    def _load_arxiv_categories(self) -> Dict[str, ResearchDomain]:
        """Map arXiv categories to research domains."""
        return {
            # Physics
            "physics": ResearchDomain.PHYSICS,
            "astro-ph": ResearchDomain.ASTRONOMY,
            "cond-mat": ResearchDomain.PHYSICS,
            "gr-qc": ResearchDomain.PHYSICS,
            "hep-ex": ResearchDomain.PHYSICS,
            "hep-lat": ResearchDomain.PHYSICS,
            "hep-ph": ResearchDomain.PHYSICS,
            "hep-th": ResearchDomain.PHYSICS,
            "math-ph": ResearchDomain.PHYSICS,
            "nlin": ResearchDomain.PHYSICS,
            "nucl-ex": ResearchDomain.PHYSICS,
            "nucl-th": ResearchDomain.PHYSICS,
            "quant-ph": ResearchDomain.PHYSICS,
            
            # Computer Science
            "cs": ResearchDomain.COMPUTER_SCIENCE,
            
            # Mathematics
            "math": ResearchDomain.MATHEMATICS,
            
            # Engineering/Applied Sciences
            "eess": ResearchDomain.ENGINEERING,
            
            # Biology
            "q-bio": ResearchDomain.BIOLOGY,
            
            # Statistics
            "stat": ResearchDomain.STATISTICS,
            
            # Economics
            "econ": ResearchDomain.ECONOMICS
        }
    
    def _build_classification_agent(self) -> Agent:
        """Build AI agent for domain classification."""
        instructions = """
You are an expert research domain classifier. Your role is to classify research papers by their primary research domains and assess relevance to user-specified domains.

# Objective
Given a paper title, abstract, and user's domain context, determine:
1. Which research domains the paper belongs to
2. How relevant it is to the user's specified domains
3. Whether it should be excluded based on domain mismatch

# Research Domains
- physics: Theoretical and experimental physics, quantum mechanics, thermodynamics
- engineering: Applied sciences, design, optimization, systems, manufacturing
- computer_science: Algorithms, AI/ML, software, hardware, data science
- mathematics: Pure and applied mathematics, statistics, mathematical modeling
- chemistry: Molecular chemistry, synthesis, catalysis, materials chemistry
- materials_science: Materials properties, characterization, synthesis, applications
- biology: Life sciences, genetics, molecular biology, ecology, evolution
- medicine: Clinical research, healthcare, medical devices, pharmaceuticals
- neuroscience: Brain research, cognitive science, neural networks (biological)
- psychology: Behavioral science, cognitive psychology, social psychology
- economics: Economic theory, econometrics, financial modeling, policy
- environmental_science: Climate, ecology, environmental monitoring, sustainability
- astronomy: Astrophysics, cosmology, planetary science, space exploration
- geosciences: Earth sciences, geology, meteorology, oceanography
- statistics: Statistical theory, data analysis, probabilistic modeling

# Classification Guidelines
1. **Primary Domain**: The main field the research contributes to
2. **Secondary Domains**: Related fields that would find this research relevant
3. **Interdisciplinary**: Papers that genuinely span multiple domains
4. **Application Context**: Consider whether it's theoretical or applied research

# Domain Relevance Assessment
For each user-specified domain, assess relevance:
- **High (0.8-1.0)**: Directly relevant, would be of high interest
- **Medium (0.5-0.7)**: Somewhat relevant, could provide useful insights
- **Low (0.2-0.4)**: Tangentially related, limited relevance
- **None (0.0-0.1)**: Not relevant, different field entirely

# Output Format
Return JSON with:
{
  "primary_domain": "domain_name",
  "secondary_domains": ["domain1", "domain2"],
  "domain_scores": {
    "domain1": 0.9,
    "domain2": 0.7
  },
  "is_relevant": true,
  "overall_relevance": 0.85,
  "exclusion_reasons": []
}

# Exclusion Criteria
Exclude papers if:
- Completely different field (e.g., astronomy paper for engineering query about vehicles)
- Pure theoretical work when applied research is needed
- Clinical/medical focus when engineering focus is needed
- Wrong scale/application (e.g., molecular when looking for macro-scale)
"""
        
        return Agent(
            name="domain_classifier",
            instructions=instructions,
            model="gpt-4o",
        )
    
    def detect_domains_from_text(self, title: str, abstract: str) -> List[ResearchDomain]:
        """Detect research domains from paper title and abstract."""
        text = f"{title} {abstract}".lower()
        domain_scores = {}
        
        for domain, patterns in self._domain_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword.lower() in text:
                    score += 2
            
            # Check methods
            for method in patterns.get("methods", []):
                if method.lower() in text:
                    score += 3  # Methods are stronger indicators
            
            # Check applications
            for app in patterns.get("applications", []):
                if app.lower() in text:
                    score += 1
            
            if score > 0:
                domain_scores[domain] = score
        
        # Return domains sorted by score, keep only significant ones
        if not domain_scores:
            return []
        
        max_score = max(domain_scores.values())
        threshold = max(2, max_score * 0.3)  # At least score 2 or 30% of max
        
        relevant_domains = [
            domain for domain, score in domain_scores.items() 
            if score >= threshold
        ]
        
        return sorted(relevant_domains, key=lambda d: domain_scores[d], reverse=True)
    
    def check_domain_exclusions(self, 
                               title: str, 
                               abstract: str, 
                               target_domains: List[ResearchDomain]) -> Tuple[bool, List[str]]:
        """Check if paper should be excluded based on domain patterns."""
        text = f"{title} {abstract}".lower()
        exclusion_reasons = []
        
        for target_domain in target_domains:
            exclusion_patterns = self._exclusion_patterns.get(target_domain, [])
            
            for pattern in exclusion_patterns:
                if pattern.lower() in text:
                    exclusion_reasons.append(f"Contains '{pattern}' - not suitable for {target_domain.value}")
        
        should_exclude = len(exclusion_reasons) > 0
        return should_exclude, exclusion_reasons
    
    async def classify_paper_domain(self, 
                                  paper_id: str,
                                  title: str, 
                                  abstract: str,
                                  domain_context: DomainContext) -> DomainClassificationResult:
        """
        Classify a paper's domain and assess relevance to user context.
        
        Args:
            paper_id: Unique identifier for the paper
            title: Paper title
            abstract: Paper abstract
            domain_context: User's domain preferences and context
            
        Returns:
            DomainClassificationResult with classification and relevance
        """
        # First, do rule-based domain detection
        detected_domains = self.detect_domains_from_text(title, abstract)
        
        # Check for exclusions
        should_exclude, exclusion_reasons = self.check_domain_exclusions(
            title, abstract, domain_context.primary_domains
        )
        
        # Use AI for more sophisticated classification if needed
        try:
            classification_prompt = f"""
Paper Title: {title}
Abstract: {abstract}

User's Primary Domains: {[d.value for d in domain_context.primary_domains]}
User's Exclude Domains: {[d.value for d in domain_context.exclude_domains]}

Classify this paper and assess its relevance to the user's domain context.
"""
            
            result = await Runner.run(self._classification_agent, classification_prompt)
            
            import json
            ai_classification = json.loads(result.final_output)
            
            # Combine rule-based and AI results
            primary_domain = ResearchDomain(ai_classification.get("primary_domain", detected_domains[0].value if detected_domains else "computer_science"))
            
            all_domains = detected_domains.copy()
            for domain_name in ai_classification.get("secondary_domains", []):
                try:
                    domain = ResearchDomain(domain_name)
                    if domain not in all_domains:
                        all_domains.append(domain)
                except ValueError:
                    continue
            
            domain_scores = {}
            for domain_name, score in ai_classification.get("domain_scores", {}).items():
                try:
                    domain = ResearchDomain(domain_name)
                    domain_scores[domain] = float(score)
                except (ValueError, TypeError):
                    continue
            
            is_relevant = ai_classification.get("is_relevant", True) and not should_exclude
            overall_relevance = ai_classification.get("overall_relevance", 0.5)
            
            if should_exclude:
                is_relevant = False
                overall_relevance = 0.0
                exclusion_reasons.extend(ai_classification.get("exclusion_reasons", []))
            
        except Exception:
            # Fallback to rule-based classification
            primary_domain = detected_domains[0] if detected_domains else ResearchDomain.COMPUTER_SCIENCE
            all_domains = detected_domains
            domain_scores = {d: 1.0 for d in detected_domains}
            
            # Simple relevance check
            is_relevant = not should_exclude and any(
                d in domain_context.primary_domains for d in detected_domains
            )
            overall_relevance = 0.7 if is_relevant else 0.1
        
        return DomainClassificationResult(
            paper_id=paper_id,
            detected_domains=all_domains,
            domain_scores=domain_scores,
            is_relevant_to_context=is_relevant,
            relevance_score=overall_relevance,
            exclusion_reasons=exclusion_reasons
        )
    
    def create_domain_context(self, 
                            primary_domains: List[str],
                            exclude_domains: Optional[List[str]] = None,
                            focus_keywords: Optional[List[str]] = None) -> DomainContext:
        """
        Create domain context from user selections.
        
        Args:
            primary_domains: List of domain names user is interested in
            exclude_domains: List of domain names to exclude
            focus_keywords: Additional keywords to focus on
            
        Returns:
            DomainContext object
        """
        primary_domain_enums = []
        for domain_name in primary_domains:
            try:
                domain = ResearchDomain(domain_name)
                primary_domain_enums.append(domain)
            except ValueError:
                continue
        
        exclude_domain_enums = []
        if exclude_domains:
            for domain_name in exclude_domains:
                try:
                    domain = ResearchDomain(domain_name)
                    exclude_domain_enums.append(domain)
                except ValueError:
                    continue
        
        # Create weights (equal weight for now, could be customized)
        domain_weights = {domain: 1.0 for domain in primary_domain_enums}
        
        return DomainContext(
            primary_domains=primary_domain_enums,
            exclude_domains=exclude_domain_enums,
            domain_weights=domain_weights,
            focus_keywords=focus_keywords or [],
            exclude_keywords=[]
        )


# Convenience functions
def get_available_domains() -> Dict[str, str]:
    """Get available research domains with display names."""
    return ResearchDomain.get_display_names()


async def classify_papers_by_domain(papers_text: str, 
                                  domain_context: DomainContext) -> List[DomainClassificationResult]:
    """
    Classify multiple papers by domain and filter based on context.
    
    Args:
        papers_text: Text containing multiple papers
        domain_context: Domain filtering context
        
    Returns:
        List of classification results for relevant papers
    """
    classifier = DomainClassifier()
    
    # Parse papers from text (reuse logic from relevance_filter)
    from .relevance_filter import RelevanceFilter
    filter_system = RelevanceFilter()
    papers = filter_system._parse_papers_from_text(papers_text)
    
    results = []
    for paper in papers:
        classification = await classifier.classify_paper_domain(
            paper_id=paper.get("paper_id", "unknown"),
            title=paper.get("title", ""),
            abstract=paper.get("abstract", ""),
            domain_context=domain_context
        )
        
        if classification.is_relevant_to_context:
            results.append(classification)
    
    return results
