"""
Controller to interface with the Netflix namespace.
"""
import logging
import time

from ..controllers BaseController

APP_NAMESPACE = "urn:x-cast:mdx-netflix-com:service:target:2"
APP_NETFLIX = "CA5E8412"

# NOTE : not used, no public API provided by Netflix so no purpose to have this...

# pylint: disable=too-many-instance-attributes
class NetflixController(BaseController):

    # pylint: disable=useless-super-delegation
    # The pylint rule useless-super-delegation doesn't realize
    # we are setting default values here.
    def __init__(self):
        super(NetflixController, self).__init__(APP_NAMESPACE, APP_NETFLIX)
        self.logger = logging.getLogger(__name__)
    # pylint: enable=useless-super-delegation
