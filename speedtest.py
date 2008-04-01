import transaction, time
from gocept.objectquery.testobjects import Dummy
from ZODB import MappingStorage, DB
from gocept.objectquery.pathexpressions import RPEQueryParser
from gocept.objectquery.collection import ObjectCollection
from gocept.objectquery.processor import QueryProcessor

def create_btree(n, c=1):
    if n < 0:
        raise ValueError("n should be >= 1")
    if n == 0:
        temp = Dummy(); temp.id = c
        return temp
    if n > 0:
        left = create_btree(n-1, c)
        right = create_btree(n-1, left.id+1)
    temp = Dummy([left, right])
    temp.id = right.id + 1
    return temp

heights = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

storage = MappingStorage.MappingStorage()
db = DB(storage)
conn = db.open()
dbroot = conn.root()
parser = RPEQueryParser()

print " h     obj  |      bi      q1      q2      q3      q4      q5  "

for n in heights:
    dbroot.clear()
    oq = ObjectCollection(conn)
    query = QueryProcessor(parser, oq)
    objects = pow(2, n+1)-1

    dbroot[0] = create_btree(n)
    transaction.commit()
    t0 = time.time()
    oq.add(dbroot[0]._p_oid)
    transaction.commit()
    t1 = time.time()
    print "%2i %8i | %7.2fs" %(n, objects, (t1-t0)),
    i = 1
    queries = ['Dummy[@id="%i"]' %(objects/2), '/Dummy', '/Dummy/Dummy/Dummy',
               'Dummy[@id="%i"]/_*/Dummy[@id="1"]' %objects,
               'Dummy[@id<"1000"]']
    for q in queries:
        t0 = time.time()
        r = query(q)
        t1 = time.time()
        print "%6.2fs" %(t1-t0),
        i = i + 1
    print ""
