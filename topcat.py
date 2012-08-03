import os
import urllib

import atpy
from sampy import SAMPHubProxy, SAMPClient

import numpy as np


class SAMPHelper(object):

    def __init__(self):

        self.myhub = SAMPHubProxy()
        self.myhub.connect()

        self.client = SAMPClient(self.myhub)

        metadata1 = {"samp.name": "Client",
                     "samp.description.text": "Client",
                     "client.version": "0.01"}

        self.client.start()
        self.client.register()

        self.client.declareMetadata(metadata1)

        self.client.bindReceiveCall("table.load.*", self._load_table)
        self.client.bindReceiveCall("table.select.*", self._select_rows)

    def _load_table(self, private_key, sender_id, msg_id, mtype, params, extra):
        print "Received table:", params['url']
        self.client.ereply(msg_id, SAMP_STATUS_OK, result = {"txt": "printed"})

    def _select_rows(self, private_key, sender_id, msg_id, mtype, params, extra):
        print "Selected rows:", params['row-list']
        self.client.ereply(msg_id, SAMP_STATUS_OK, result = {"txt": "printed"})

    def send_table(self, filename):
        '''
        Send a table via SAMP

        Parameters
        ----------
        filename : str
            The table to send
        '''

        result = self.myhub.notifyAll(self.client.getPrivateKey(),
                    {"samp.mtype": "table.load.votable",
                     "samp.params": {"url": 'file://' + os.path.abspath(filename),
                                     "name": filename}
                    })

        return result[0]

    def select_rows(self, table_id, rows):

        result = self.myhub.notifyAll(self.client.getPrivateKey(),
                    {"samp.mtype": "table.select.rowList",
                     "samp.params": {"table-id": table_id,
                                     "row-list": rows}
                    })

    def finalize(self):

        self.client.unregister()
        self.client.stop()

        self.myhub.disconnect()

if __name__ == "__main__":

    t = atpy.Table()
    t.add_column('id', range(10))
    t.add_column('flux', np.random.random(10))
    t.write('test.xml', overwrite=True)

    try:
        h = SAMPHelper()
        tid = h.send_table('test.xml')
        h.select_rows(tid, ["1", "3", "4"])
    finally:
        h.finalize()
