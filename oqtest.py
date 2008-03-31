import transaction, time
from gocept.objectquery.testobjects import Dummy
from ZODB import MappingStorage, DB
from persistent import Persistent
from gocept.objectquery.pathexpressions import RPEQueryParser
from gocept.objectquery.collection import ObjectCollection
from gocept.objectquery.processor import QueryProcessor

def fill_db_width(n):
    dbroot.clear()
    objects = ObjectCollection(conn)
    for i in xrange(n):
        dbroot[i] = Dummy([Dummy([Dummy()]), Dummy()])
        dbroot[i].id = i
    transaction.commit()
    t0 = time.clock()
    for i in xrange(n):
        objects.add(dbroot[i]._p_oid, dbroot._p_oid)
    transaction.commit()
    t1 = time.clock()
    print "Duration for inserting %i items: %is" %((n*4),(t1-t0))

recsize = [250,1250,2500,12500,25000,50000,100000,150000,200000,250000]

for n in recsize:
    storage = MappingStorage.MappingStorage()
    db = DB(storage)
    conn = db.open()
    dbroot = conn.root()
    parser = RPEQueryParser()
    objects = ObjectCollection(conn)
    query = QueryProcessor(parser, objects)

    fill_db_width(n)
