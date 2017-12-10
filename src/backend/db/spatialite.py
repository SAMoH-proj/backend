## Generic access to *native* spatialite instance (avoid fickle python wrappers)
## NOTE: depends spatialite dynamic library `libsqlite3-mod-spatialite'
##
## Usage:
##      import spatialite
##      output = spatialite.execute("select HEX(GeomFromText(?));",
##                                  ('POINT(788703.57 4645636.3)',))
## The output is a a tuple of lists. To get the 2nd field from 3rd row just use output[2][1] (0-based index)

import sqlite3.dbapi2 as db

from backend import config

### Constants ###

# full path of sqlite3 database
DB = config.get("path", "geodb")

# full path of libspatialite.so.7
SPATIALPLUGIN = config.get("path", "libspatialite")
# creating/connecting the test_db
con = db.connect(DB, check_same_thread=False)
con.enable_load_extension(True)
con.load_extension(SPATIALPLUGIN)
con.enable_load_extension(False)


def execute(sql, args=()):
    """
        Execute sql using args for sql substitution

        Args:
            sql:  SQL statement
            args (optional) : list of susbtitution values
    """
    res = con.execute(sql, args)
    con.commit()
    return res.fetchall()


def get_tables():
    """
        Equivalent to ".tables" using the sqlite3 CLI
    """
    return execute("SELECT name FROM sqlite_master WHERE type = 'table';")


# Example:
if __name__ == "__main__":
    # Test that geometry functions work
    # print get_tables()
    print(execute("select HEX(GeomFromText(?));", ('POINT(788703.57 4645636.3)',)))

#################
