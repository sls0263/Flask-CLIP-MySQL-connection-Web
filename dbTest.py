import pymysql

#db connect
db = pymysql.connect(host="localhost",
user="root", password="1234",
charset="utf8")
cursor = db.cursor()

cursor.execute('use smartproject;')
cursor.execute('INSERT INTO shop_product (name, price, detail) value ("java", "1000", "detail")')

db.commit()
db.close()