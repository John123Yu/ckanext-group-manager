with open("/tmp/python.log", "a") as mylog:
    mylog.write("\n%s\n" % "HELLO")

import collections
import logging
from ckan.lib.base import (BaseController, c, g, render, request, response, abort)

class GroupManager(BaseController):

    def index(self):
        return render('group_manager/index.html')
