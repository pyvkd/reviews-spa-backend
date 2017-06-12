import sqlite3
import argparse


def main(dbname, tablename):
    with sqlite3.connect(dbname) as conn:
        c = conn.cursor()
        query = """CREATE TABLE %s(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        rating INTEGER,
        review BLOB,
        createdon TEXT
        )
        """ % (tablename)
        c.execute(query)
        conn.commit()
    with open('.env', 'w') as fp:
        wr = "DBNAME=%s\nTABLENAME=%s\n" % (dbname, tablename)
        fp.write(wr)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap = argparse.ArgumentParser(description='Creating Sqlite3 DB and relevant table')
    ap.add_argument('dbname', metavar='DBNAME', type=str, nargs='+',
                    help='dbname to create')
    ap.add_argument('--table', dest='tablename', default='review',
                    help='tablename (default review)')
    args = ap.parse_args()
    main(args.dbname[0], args.tablename)
