import subprocess
import re
import datetime
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker

NS_QUERY_CMD = \
    'dig +nostats +nocomments +nocmd -b 127.0.0.1 @localhost {} axfr'

engine = create_engine('sqlite:///ddns-test.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Record(Base):
    __tablename__ = 'record'
    record_id = Column(Integer, primary_key=True)
    SOA_serial = Column(Integer)
    FQDN = Column(String)
    TTL = Column(Integer)
    type = Column(String)
    value = Column(String)
    create_time = Column(DateTime)
    created_by = Column(Integer, ForeignKey('user.uid'))
    zone = Column(Integer, ForeignKey('zone.zone_id'))

    # def __init__(self, _id, SOA_serial, FQDN, TTL, _type, value,
    #              created_by, zone, create_time=False):
    #     self._id = _id
    #     self.SOA_serial = SOA_serial
    #     self.FQDN = FQDN
    #     self.TTL = TTL
    #     self._type = _type
    #     self.value = value
    #     self.created_by = created_by
    #     self.zone = zone
    #     self.create_time = create_time

    def __repr__(self):
        return '<Record(id={}, SOA_serial={}, FQDN={}, type={}, value={})>' \
               .format(self.record_id, self.SOA_serial,
                       self.FQDN, self.type, self.value)


class Zone(Base):
    __tablename__ = 'zone'
    zone_id = Column(Integer, primary_key=True)
    created_by = Column(Integer, ForeignKey('user.uid'))
    domain = Column(String)
    name = Column(String)
    # def __init__(self, _id, name, domain, created_by):
    #     self.records = []
    #     self.domain = domain
    #     self.name = name
    #     self.created_by = created_by

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
        SOA_serial = records[0][4].split()[0]
        i = 0
        for record in records:
            obj = Record(
                    record_id=i,
                    SOA_serial=SOA_serial,
                    FQDN=record[0],
                    TTL=record[1],
                    type=record[3],
                    value=record[4],
                    create_time=datetime.datetime.now(),
                    created_by=-1,
                    zone=1
                    )
            session.add(obj)
            i += 1
        session.commit()


class User(Base):
    __tablename__ = 'user'
    uid = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    email = Column(String)
    password = Column(String)


class NsupdateTransaction:
    def __init__(self):
        self.statements = []
        pass

    # execute nsupdate
    def execute(self):
        pass


if __name__ == '__main__':
    # create schema
    Base.metadata.create_all(engine)

    anonymousUser = User(uid=-1, username='unknown',
                         name='unknown', email='unknown')
    test_zone = Zone(zone_id=1, created_by=-1,
                     domain='bopa.ng', name='test_zone')
    session.add(anonymousUser)
    session.add(test_zone)
    session.commit()
    test_zone.refresh()
