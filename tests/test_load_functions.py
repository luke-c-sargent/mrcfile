# Copyright (c) 2016, Science and Technology Facilities Council
# This software is distributed under a BSD licence. See LICENSE.txt.

"""
Tests for mrcfile __init__.py loading functions.
"""

# Import Python 3 features for future-proofing
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import tempfile
import unittest

import numpy as np

import mrcfile
from . import helpers


class LoadFunctionTest(helpers.AssertRaisesRegexMixin, unittest.TestCase):
    
    """Unit tests for MRC loading functions.
    
    """
    
    def setUp(self):
        super(LoadFunctionTest, self).setUp()
        
        # Set up test files and names to be used
        self.test_data = helpers.get_test_data_path()
        self.test_output = tempfile.mkdtemp()
        self.temp_mrc_name = os.path.join(self.test_output, 'test_mrcfile.mrc')
        self.example_mrc_name = os.path.join(self.test_data, 'EMD-3197.map')
        self.gzip_mrc_name = os.path.join(self.test_data, 'emd_3197.map.gz')
    
    def test_normal_opening(self):
        with mrcfile.open(self.example_mrc_name) as mrc:
            assert repr(mrc) == ("MrcFile('{0}', mode='r')"
                                 .format(self.example_mrc_name))
    
    def test_gzip_opening(self):
        with mrcfile.open(self.gzip_mrc_name) as mrc:
            assert repr(mrc) == ("GzipMrcFile('{0}', mode='r')"
                                 .format(self.gzip_mrc_name))
    
    def test_mmap_opening(self):
        with mrcfile.mmap(self.example_mrc_name) as mrc:
            assert repr(mrc) == ("MrcMemmap('{0}', mode='r')"
                                 .format(self.example_mrc_name))
    
    def test_new_empty_file(self):
        with mrcfile.new(self.temp_mrc_name) as mrc:
            assert repr(mrc) == ("MrcFile('{0}', mode='w+')"
                                 .format(self.temp_mrc_name))
    
    def test_new_file_with_data(self):
        data = np.arange(24, dtype=np.uint16).reshape(2, 3, 4)
        with mrcfile.new(self.temp_mrc_name, data) as mrc:
            np.testing.assert_array_equal(data, mrc.data)
    
    def test_new_gzip_file(self):
        data = np.arange(24, dtype=np.uint16).reshape(4, 3, 2)
        with mrcfile.new(self.temp_mrc_name, data, gzip=True) as mrc:
            np.testing.assert_array_equal(data, mrc.data)
            assert repr(mrc) == ("GzipMrcFile('{0}', mode='w+')"
                                 .format(self.temp_mrc_name))
    
    def test_overwriting_flag(self):
        assert not os.path.exists(self.temp_mrc_name)
        open(self.temp_mrc_name, 'w+').close()
        assert os.path.exists(self.temp_mrc_name)
        with self.assertRaisesRegex(IOError, "already exists"):
            mrcfile.new(self.temp_mrc_name)
        with self.assertRaisesRegex(IOError, "already exists"):
            mrcfile.new(self.temp_mrc_name, overwrite=False)
        mrcfile.new(self.temp_mrc_name, overwrite=True).close()
    
    def test_invalid_mode_raises_exception(self):
        with (self.assertRaisesRegex(ValueError, "Mode 'z' not supported")):
            mrcfile.open(self.example_mrc_name, mode='z')
    
    def test_non_mrc_file_raises_exception(self):
        name = os.path.join(self.test_data, 'emd_3197.png')
        with (self.assertRaisesRegex(ValueError, 'Map ID string not found')):
            mrcfile.open(name)
    
    def test_gzipped_non_mrc_file_raises_exception(self):
        name = os.path.join(self.test_data, 'emd_3197.png.gz')
        with (self.assertRaisesRegex(ValueError, 'Map ID string not found')):
            mrcfile.open(name)
    
    def test_error_in_gzip_opening_raises_new_exception(self):
        # Tricky to test this case. Easiest to monkey-patch GzipMrcFile.__init__
        old_init = mrcfile.GzipMrcFile.__init__
        try:
            msg = 'Fake error: valid gzip file with invalid MRC data'
            def error(*args, **kwargs):
                raise IOError(msg)
            mrcfile.GzipMrcFile.__init__ = error
            with self.assertRaisesRegex(IOError, msg):
                mrcfile.open(self.gzip_mrc_name)
        finally:
            mrcfile.GzipMrcFile.__init__ = old_init


if __name__ == '__main__':
    unittest.main()