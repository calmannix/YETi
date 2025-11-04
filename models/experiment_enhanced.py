"""Enhanced experiment model with variant support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from experiment_manager import Experiment, ExperimentStatus
from models.variant import VideoVariant, VariantType


@dataclass
class EnhancedExperiment(Experiment):
    """
    Extended experiment model with variant support and enhanced features.
    
    Backward compatible with the original Experiment class.
    """
    
    # Variants for A/B testing
    variants: List[VideoVariant] = field(default_factory=list)
    
    # Experiment configuration
    sample_size_target: Optional[int] = None  # Target number of views/impressions
    confidence_level: float = 0.95  # Statistical confidence level (95%)
    
    # Tracking
    current_sample_size: int = 0
    last_data_fetch: Optional[str] = None
    
    # Analytics
    statistical_significance: Optional[Dict] = None
    winner_variant_id: Optional[str] = None
    
    # Automation
    auto_stop_on_significance: bool = False
    auto_pick_winner: bool = False
    
    def add_variant(self, variant: VideoVariant):
        """Add a variant to the experiment."""
        self.variants.append(variant)
    
    def get_variant(self, variant_id: str) -> Optional[VideoVariant]:
        """Get variant by ID."""
        for variant in self.variants:
            if variant.id == variant_id:
                return variant
        return None
    
    def get_control_variant(self) -> Optional[VideoVariant]:
        """Get the control variant."""
        for variant in self.variants:
            if variant.is_control:
                return variant
        return None
    
    def get_treatment_variants(self) -> List[VideoVariant]:
        """Get all treatment (non-control) variants."""
        return [v for v in self.variants if not v.is_control]
    
    def has_significant_result(self) -> bool:
        """Check if experiment has statistically significant results."""
        if not self.statistical_significance:
            return False
        return self.statistical_significance.get('is_significant', False)
    
    def get_winning_variant(self) -> Optional[VideoVariant]:
        """Get the winning variant if determined."""
        if self.winner_variant_id:
            return self.get_variant(self.winner_variant_id)
        return None
    
    def calculate_progress(self) -> float:
        """Calculate experiment progress as percentage."""
        if not self.sample_size_target:
            # Use date-based progress
            start = datetime.fromisoformat(self.start_date)
            end = datetime.fromisoformat(self.end_date)
            now = datetime.now()
            
            if now < start:
                return 0.0
            elif now > end:
                return 100.0
            
            total_duration = (end - start).total_seconds()
            elapsed = (now - start).total_seconds()
            return (elapsed / total_duration) * 100
        else:
            # Use sample size progress
            if self.sample_size_target == 0:
                return 0.0
            progress = (self.current_sample_size / self.sample_size_target) * 100
            return min(progress, 100.0)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary with variant data."""
        result = super().to_dict()
        result.update({
            'variants': [v.to_dict() for v in self.variants],
            'sample_size_target': self.sample_size_target,
            'confidence_level': self.confidence_level,
            'current_sample_size': self.current_sample_size,
            'last_data_fetch': self.last_data_fetch,
            'statistical_significance': self.statistical_significance,
            'winner_variant_id': self.winner_variant_id,
            'auto_stop_on_significance': self.auto_stop_on_significance,
            'auto_pick_winner': self.auto_pick_winner,
            'progress': self.calculate_progress()
        })
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedExperiment':
        """Create enhanced experiment from dictionary."""
        # Import here to avoid circular dependency
        from experiment_manager import SuccessCriteria
        
        # Parse variants
        variants = []
        if 'variants' in data:
            variants = [VideoVariant.from_dict(v) for v in data['variants']]
        
        return cls(
            id=data['id'],
            name=data['name'],
            hypothesis=data['hypothesis'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            metrics=data['metrics'],
            success_criteria=SuccessCriteria.from_dict(data['success_criteria']),
            status=ExperimentStatus(data.get('status', 'draft')),
            baseline_start=data.get('baseline_start'),
            baseline_end=data.get('baseline_end'),
            video_ids=data.get('video_ids'),
            notes=data.get('notes', ''),
            results=data.get('results'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            variants=variants,
            sample_size_target=data.get('sample_size_target'),
            confidence_level=data.get('confidence_level', 0.95),
            current_sample_size=data.get('current_sample_size', 0),
            last_data_fetch=data.get('last_data_fetch'),
            statistical_significance=data.get('statistical_significance'),
            winner_variant_id=data.get('winner_variant_id'),
            auto_stop_on_significance=data.get('auto_stop_on_significance', False),
            auto_pick_winner=data.get('auto_pick_winner', False)
        )
    
    @classmethod
    def from_experiment(cls, experiment: Experiment) -> 'EnhancedExperiment':
        """Convert a standard Experiment to EnhancedExperiment."""
        return cls(
            id=experiment.id,
            name=experiment.name,
            hypothesis=experiment.hypothesis,
            start_date=experiment.start_date,
            end_date=experiment.end_date,
            metrics=experiment.metrics,
            success_criteria=experiment.success_criteria,
            status=experiment.status,
            baseline_start=experiment.baseline_start,
            baseline_end=experiment.baseline_end,
            video_ids=experiment.video_ids,
            notes=experiment.notes,
            results=experiment.results,
            created_at=experiment.created_at
        )


