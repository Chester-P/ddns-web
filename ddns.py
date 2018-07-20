import subprocess
import re
import datetime
import sys

NS_QUERY_CMD = \
    'dig +nostats +nocomments +nocmd -b 127.0.0.1 @localhost {} axfr'


class Record:
    def __init__(self, _id, SOA_serial, FQDN, TTL, _type, value,
                 created_by, zone, create_time=False):
        self._id = _id
        self.SOA_serial = SOA_serial
        self.FQDN = FQDN
        self.TTL = TTL
        self._type = _type
        self.value = value
        self.created_by = created_by
        self.zone = zone
        self.create_time = create_time


class Zone:
    def __init__(self, _id, name, domain, created_by):
        self.records = []
        self.domain = domain
        self.name = name
        self.created_by = created_by

    def addRecord(self, Record):
        pass

    # Erase all current records and read records from axfr zone transfer
    # Ideally, this would never be excuted as all changes to a zone
    # goes through this program
    def refresh(self):
        try:
            output = subprocess.check_output(
                    NS_QUERY_CMD.format(self.domain).split())
        except subprocess.CalledProcessError as err:
            print('dig failed with exit status: ', err.returncode,
                  file=sys.stderr)
            sys.exit()

        records = [re.split('\t+', line)
                   for line in output.decode().split('\n') if line]
        assert(records)
        self.records.clear()
        SOA_serial = records[0][4].split()[0]
        i = 0
        for record in records:
            obj = Record(i, SOA_serial, record[0], record[1],
                         record[3], record[4], -1, self,
                         datetime.datetime.now)
            self.records.append(obj)
            i += 1

class NsupdateTransaction:
    def __init__(self):
        self.statements = []
        pass

    # execute nsupdate
    def execute(self):
        pass
