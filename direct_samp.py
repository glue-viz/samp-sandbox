import os
import xmlrpclib

import atpy
import numpy as np

lockfile = os.path.expanduser('~/.samp')
if not os.path.exists(lockfile):
    raise Exception("Hub is not running")
else:
    HUB_PARAMS = {}
    for line in open(lockfile):
        if not line.startswith('#'):
            key, value = line.split('=', 1)
            HUB_PARAMS[key] = value.strip()

# Set up proxy
s = xmlrpclib.ServerProxy(HUB_PARAMS['samp.hub.xmlrpc.url'])

# Register with Hub
result = s.samp.hub.register(HUB_PARAMS['samp.secret'])
private_key = result['samp.private-key']

# Create test table
t = atpy.Table()
t.add_column('id', range(10))
t.add_column('flux', np.random.random(10))
t.write('test.xml', overwrite=True)

# Send table
message = {}
message['samp.mtype'] = "table.load.votable"
message['samp.params'] = {}
message['samp.params']['url'] = 'file://' + os.path.abspath('test.xml')
message['samp.params']['name'] = 'test'

s.samp.hub.notifyAll(private_key, message)
