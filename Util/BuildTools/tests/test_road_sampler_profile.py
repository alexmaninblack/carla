import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('road_sampler_profile', Path(__file__).parents[1] / 'road_sampler_profile.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.valid = dict(address_x='TA_WRAP', address_y='TA_WRAP', filter='TF_DEFAULT',
                          lod_group='TEXTUREGROUP_WORLD', virtual_texture_streaming=False)

    def test_expected_settings(self):
        profile.require_compatible(self.valid)

    def test_incompatible_settings_fail_closed(self):
        for key, value in [('address_x', 'TA_CLAMP'), ('address_y', 'TA_MIRROR'),
                           ('filter', 'TF_NEAREST'), ('lod_group', 'TEXTUREGROUP_WORLD_NORMAL_MAP'),
                           ('virtual_texture_streaming', True)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                profile.require_compatible(dict(self.valid, **{key: value}))

    def test_profile_is_narrow(self):
        self.assertEqual(len(set(profile.NODES)), 6)
        self.assertNotIn('MaterialExpressionTextureSample_11', profile.NODES)
        self.assertNotIn('MaterialExpressionTextureSampleParameter2D_9', profile.NODES)
        self.assertEqual(len(set(profile.INSTANCES)), 5)
