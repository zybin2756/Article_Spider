import os
import sys
from scrapy.cmdline import execute

dirname = os.path.dirname(os.path.abspath(__file__))

sys.path.append(dirname)

execute(["scrapy","crawl","zhihu"])