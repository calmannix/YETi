"""Video variant models for A/B testing."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime


class VariantType(Enum):
    """Types of video variants that can be tested."""
    THUMBNAIL = "thumbnail"
    TITLE = "title"
    DESCRIPTION = "description"
    UPLOAD_TIME = "upload_time"
    VIDEO_LENGTH = "video_length"
    INTRO = "intro"
    OUTRO = "outro"
    TAGS = "tags"
    CUSTOM = "custom"


@dataclass
class VideoVariant:
    """
    Represents a variant of a video element for A/B testing.
    
    For example:
    - Variant A: Bold red thumbnail
    - Variant B: Minimal blue thumbnail
    """
    id: str
    experiment_id: str
    variant_type: VariantType
    name: str  # e.g., "Bold Red Thumbnail", "Short Title Version"
    description: str = ""
    
    # Variant-specific data
    data: Dict = field(default_factory=dict)
    
    # Video IDs this variant applies to
    video_ids: List[str] = field(default_factory=list)
    
    # Traffic allocation (percentage, 0-100)
    traffic_allocation: float = 50.0
    
    # Performance tracking
    impressions: int = 0
    clicks: int = 0
    views: int = 0
    
    # Metadata
    is_control: bool = False  # Is this the control/baseline variant?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    activated_at: Optional[str] = None
    deactivated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VideoVariant':
        """Create variant from dictionary."""
        return cls(
            id=data['id'],
            experiment_id=data['experiment_id'],
            variant_type=VariantType(data['variant_type']),
            name=data['name'],
            description=data.get('description', ''),
            data=data.get('data', {}),
            video_ids=data.get('video_ids', []),
            traffic_allocation=data.get('traffic_allocation', 50.0),
            impressions=data.get('impressions', 0),
            clicks=data.get('clicks', 0),
            views=data.get('views', 0),
            is_control=data.get('is_control', False),
            created_at=data.get('created_at', datetime.now().isoformat()),
            activated_at=data.get('activated_at'),
            deactivated_at=data.get('deactivated_at')
        )
    
    def to_dict(self) -> Dict:
        """Convert variant to dictionary."""
        result = asdict(self)
        result['variant_type'] = self.variant_type.value
        return result
    
    def get_ctr(self) -> float:
        """Calculate click-through rate."""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100
    
    def get_view_rate(self) -> float:
        """Calculate view rate from clicks."""
        if self.clicks == 0:
            return 0.0
        return (self.views / self.clicks) * 100
    
    def is_active(self) -> bool:
        """Check if variant is currently active."""
        return self.activated_at is not None and self.deactivated_at is None


@dataclass
class ThumbnailVariant:
    """Specialized variant for thumbnail testing."""
    thumbnail_url: str
    thumbnail_path: Optional[str] = None
    style_description: str = ""  # e.g., "Bold text, red background"
    colors: List[str] = field(default_factory=list)
    has_text: bool = True
    has_face: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage in VideoVariant.data."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThumbnailVariant':
        """Create from dictionary."""
        return cls(
            thumbnail_url=data['thumbnail_url'],
            thumbnail_path=data.get('thumbnail_path'),
            style_description=data.get('style_description', ''),
            colors=data.get('colors', []),
            has_text=data.get('has_text', True),
            has_face=data.get('has_face', False)
        )


@dataclass
class TitleVariant:
    """Specialized variant for title testing."""
    title_text: str
    character_count: int = 0
    has_numbers: bool = False
    has_emoji: bool = False
    has_question: bool = False
    sentiment: str = "neutral"  # positive, negative, neutral
    
    def __post_init__(self):
        """Calculate derived fields."""
        if not self.character_count:
            self.character_count = len(self.title_text)
        
        import re
        self.has_numbers = bool(re.search(r'\d', self.title_text))
        self.has_emoji = bool(re.search(r'[^\w\s,.\-!?]', self.title_text))
        self.has_question = '?' in self.title_text
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TitleVariant':
        """Create from dictionary."""
        return cls(
            title_text=data['title_text'],
            character_count=data.get('character_count', len(data['title_text'])),
            has_numbers=data.get('has_numbers', False),
            has_emoji=data.get('has_emoji', False),
            has_question=data.get('has_question', False),
            sentiment=data.get('sentiment', 'neutral')
        )


class VariantManager:
    """Manage variants for experiments."""
    
    def __init__(self):
        self.variants: Dict[str, VideoVariant] = {}
    
    def create_variant(
        self,
        experiment_id: str,
        variant_type: VariantType,
        name: str,
        video_ids: List[str],
        **kwargs
    ) -> VideoVariant:
        """Create a new variant."""
        variant_id = f"{experiment_id}_{variant_type.value}_{len(self.variants)}"
        
        variant = VideoVariant(
            id=variant_id,
            experiment_id=experiment_id,
            variant_type=variant_type,
            name=name,
            video_ids=video_ids,
            **kwargs
        )
        
        self.variants[variant_id] = variant
        return variant
    
    def get_variants_for_experiment(self, experiment_id: str) -> List[VideoVariant]:
        """Get all variants for an experiment."""
        return [
            v for v in self.variants.values() 
            if v.experiment_id == experiment_id
        ]
    
    def get_active_variants(self, experiment_id: str) -> List[VideoVariant]:
        """Get active variants for an experiment."""
        return [
            v for v in self.get_variants_for_experiment(experiment_id)
            if v.is_active()
        ]
    
    def activate_variant(self, variant_id: str):
        """Mark variant as active."""
        if variant_id in self.variants:
            self.variants[variant_id].activated_at = datetime.now().isoformat()
            self.variants[variant_id].deactivated_at = None
    
    def deactivate_variant(self, variant_id: str):
        """Mark variant as inactive."""
        if variant_id in self.variants:
            self.variants[variant_id].deactivated_at = datetime.now().isoformat()


