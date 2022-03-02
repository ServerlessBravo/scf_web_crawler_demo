import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)

## for import common module
common_dir = os.path.join(parent_dir, '..')
sys.path.append(common_dir)

from .tasks import *