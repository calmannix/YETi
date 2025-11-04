"""Unit tests for video variant system."""

import unittest
from datetime import datetime
from models.variant import (
    VideoVariant, VariantType, VariantManager,
    ThumbnailVariant, TitleVariant
)


class TestVideoVariant(unittest.TestCase):
    """Test cases for VideoVariant class."""
    
    def test_variant_creation(self):
        """Test creating a basic variant."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Red Thumbnail',
            description='Bold red background',
            video_ids=['VIDEO_1', 'VIDEO_2']
        )
        
        self.assertEqual(variant.id, 'var_001')
        self.assertEqual(variant.experiment_id, 'exp_001')
        self.assertEqual(variant.variant_type, VariantType.THUMBNAIL)
        self.assertEqual(variant.name, 'Red Thumbnail')
        self.assertEqual(len(variant.video_ids), 2)
        self.assertFalse(variant.is_control)
    
    def test_variant_types(self):
        """Test all variant types."""
        types = [
            VariantType.THUMBNAIL,
            VariantType.TITLE,
            VariantType.DESCRIPTION,
            VariantType.UPLOAD_TIME,
            VariantType.VIDEO_LENGTH,
            VariantType.INTRO,
            VariantType.OUTRO,
            VariantType.TAGS,
            VariantType.CUSTOM
        ]
        
        for var_type in types:
            variant = VideoVariant(
                id=f'var_{var_type.value}',
                experiment_id='exp_001',
                variant_type=var_type,
                name=f'Test {var_type.value}'
            )
            self.assertEqual(variant.variant_type, var_type)
    
    def test_variant_ctr_calculation(self):
        """Test CTR calculation."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test',
            impressions=1000,
            clicks=150
        )
        
        ctr = variant.get_ctr()
        self.assertEqual(ctr, 15.0)
    
    def test_variant_ctr_zero_impressions(self):
        """Test CTR with zero impressions."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test',
            impressions=0,
            clicks=0
        )
        
        ctr = variant.get_ctr()
        self.assertEqual(ctr, 0.0)
    
    def test_variant_view_rate_calculation(self):
        """Test view rate calculation."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test',
            clicks=100,
            views=80
        )
        
        view_rate = variant.get_view_rate()
        self.assertEqual(view_rate, 80.0)
    
    def test_variant_is_active(self):
        """Test active status checking."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test'
        )
        
        # Not active initially
        self.assertFalse(variant.is_active())
        
        # Activate
        variant.activated_at = datetime.now().isoformat()
        self.assertTrue(variant.is_active())
        
        # Deactivate
        variant.deactivated_at = datetime.now().isoformat()
        self.assertFalse(variant.is_active())
    
    def test_variant_to_dict(self):
        """Test variant serialization to dict."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test',
            video_ids=['VIDEO_1']
        )
        
        data = variant.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['id'], 'var_001')
        self.assertEqual(data['variant_type'], 'thumbnail')
        self.assertEqual(data['name'], 'Test')
    
    def test_variant_from_dict(self):
        """Test variant deserialization from dict."""
        data = {
            'id': 'var_001',
            'experiment_id': 'exp_001',
            'variant_type': 'thumbnail',
            'name': 'Test',
            'video_ids': ['VIDEO_1'],
            'traffic_allocation': 50.0,
            'is_control': True
        }
        
        variant = VideoVariant.from_dict(data)
        
        self.assertEqual(variant.id, 'var_001')
        self.assertEqual(variant.variant_type, VariantType.THUMBNAIL)
        self.assertTrue(variant.is_control)


class TestThumbnailVariant(unittest.TestCase):
    """Test cases for ThumbnailVariant class."""
    
    def test_thumbnail_variant_creation(self):
        """Test creating thumbnail variant."""
        thumb = ThumbnailVariant(
            thumbnail_url='https://example.com/thumb.jpg',
            style_description='Bold red background',
            colors=['red', 'yellow'],
            has_text=True,
            has_face=False
        )
        
        self.assertEqual(thumb.thumbnail_url, 'https://example.com/thumb.jpg')
        self.assertEqual(len(thumb.colors), 2)
        self.assertTrue(thumb.has_text)
        self.assertFalse(thumb.has_face)
    
    def test_thumbnail_serialization(self):
        """Test thumbnail to/from dict."""
        thumb = ThumbnailVariant(
            thumbnail_url='https://example.com/thumb.jpg',
            colors=['red']
        )
        
        data = thumb.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn('thumbnail_url', data)
        
        thumb2 = ThumbnailVariant.from_dict(data)
        self.assertEqual(thumb2.thumbnail_url, thumb.thumbnail_url)


class TestTitleVariant(unittest.TestCase):
    """Test cases for TitleVariant class."""
    
    def test_title_variant_creation(self):
        """Test creating title variant."""
        title = TitleVariant(
            title_text='How to Code in Python 🐍'
        )
        
        self.assertEqual(title.character_count, len('How to Code in Python 🐍'))
        self.assertFalse(title.has_numbers)
        self.assertTrue(title.has_emoji)
        self.assertFalse(title.has_question)
    
    def test_title_with_numbers(self):
        """Test title detection of numbers."""
        title = TitleVariant(title_text='Top 10 Tips')
        self.assertTrue(title.has_numbers)
    
    def test_title_with_question(self):
        """Test title detection of questions."""
        title = TitleVariant(title_text='How does this work?')
        self.assertTrue(title.has_question)
    
    def test_title_serialization(self):
        """Test title to/from dict."""
        title = TitleVariant(title_text='Test Title')
        
        data = title.to_dict()
        self.assertIsInstance(data, dict)
        
        title2 = TitleVariant.from_dict(data)
        self.assertEqual(title2.title_text, title.title_text)


class TestVariantManager(unittest.TestCase):
    """Test cases for VariantManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = VariantManager()
    
    def test_create_variant(self):
        """Test creating variant through manager."""
        variant = self.manager.create_variant(
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Red Thumbnail',
            video_ids=['VIDEO_1']
        )
        
        self.assertIsInstance(variant, VideoVariant)
        self.assertIn(variant.id, self.manager.variants)
    
    def test_get_variants_for_experiment(self):
        """Test retrieving variants for specific experiment."""
        # Create variants for multiple experiments
        self.manager.create_variant('exp_001', VariantType.THUMBNAIL, 'Var1', [])
        self.manager.create_variant('exp_001', VariantType.THUMBNAIL, 'Var2', [])
        self.manager.create_variant('exp_002', VariantType.TITLE, 'Var3', [])
        
        exp_001_variants = self.manager.get_variants_for_experiment('exp_001')
        
        self.assertEqual(len(exp_001_variants), 2)
        for var in exp_001_variants:
            self.assertEqual(var.experiment_id, 'exp_001')
    
    def test_get_active_variants(self):
        """Test retrieving only active variants."""
        var1 = self.manager.create_variant('exp_001', VariantType.THUMBNAIL, 'Var1', [])
        var2 = self.manager.create_variant('exp_001', VariantType.THUMBNAIL, 'Var2', [])
        
        # Activate only var1
        self.manager.activate_variant(var1.id)
        
        active = self.manager.get_active_variants('exp_001')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, var1.id)
    
    def test_activate_deactivate_variant(self):
        """Test variant activation and deactivation."""
        variant = self.manager.create_variant('exp_001', VariantType.THUMBNAIL, 'Test', [])
        
        # Activate
        self.manager.activate_variant(variant.id)
        self.assertIsNotNone(self.manager.variants[variant.id].activated_at)
        
        # Deactivate
        self.manager.deactivate_variant(variant.id)
        self.assertIsNotNone(self.manager.variants[variant.id].deactivated_at)


class TestVariantEdgeCases(unittest.TestCase):
    """Test edge cases for variant system."""
    
    def test_variant_with_custom_data(self):
        """Test variant with custom data field."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.CUSTOM,
            name='Custom Test',
            data={'custom_field': 'custom_value', 'number': 42}
        )
        
        self.assertEqual(variant.data['custom_field'], 'custom_value')
        self.assertEqual(variant.data['number'], 42)
    
    def test_variant_traffic_allocation(self):
        """Test traffic allocation values."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test',
            traffic_allocation=30.0
        )
        
        self.assertEqual(variant.traffic_allocation, 30.0)
    
    def test_variant_with_no_video_ids(self):
        """Test variant without video IDs."""
        variant = VideoVariant(
            id='var_001',
            experiment_id='exp_001',
            variant_type=VariantType.THUMBNAIL,
            name='Test'
        )
        
        self.assertEqual(len(variant.video_ids), 0)


if __name__ == '__main__':
    unittest.main()





