import MySQLdb
db = MySQLdb.connect('localhost', 'admin', 'admin', 'xc_net',charset='utf8')
# cur = db.cursor()
# cur.execute('select * from cnu_total_copy where ID = 1')
# for aa in cur.description:
#   print aa
print db.query('select * from cnu_total_copy')