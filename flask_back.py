from flask import Flask, render_template, url_for, request, jsonify
from geopy.distance import geodesic as GD
import sqlite3



app = Flask(__name__)



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        req = request.json
        print(req)
    conn = sqlite3.connect("justUp.db")
    cursor = conn.cursor()
    for title, in cursor.execute('SELECT mail FROM users WHERE mail LIKE ?', [req['email']]):
        print(title)
    return 'Hello'


@app.route("/sign_in-flask", methods=["POST", "GET"])
def sign_in_flask():
    if request.method == 'POST':
        req = request.json
        print(req)
    conn = sqlite3.connect("justUp.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO about_user_history VALUES (1,'{req['transport']}', '{req['climate']}', '{req['type']}','{req['adults']}', '{req['childs']}', '{req['pets']}', '{req['money']}', '{req['dista']}', '{req['distb']}', '{req['date']}', '{req['duration']}')")
    conn.commit()
    return 'None'
@app.route("/near", methods=["POST"])
def near():
    if request.method == 'POST':
        req = request.json
        print(req)
    g = (57.624758, 39.884910)
    print(g)
    try:
        sqlite_connection = sqlite3.connect('justUp.db')

        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from places"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк: ", len(records))
        print("Вывод каждой строки")
        mins = []
        print(records)
        for row in records:
            mins.append(GD(g, (row[6], row[7])))
        mins_num = list(enumerate(mins, 0))

        t_min = min(mins_num, key=lambda i: i[1])
        if GD(g, (records[t_min[0]][6], records[t_min[0]][7])).m <= 2500:
            print(records[t_min[0]][2] + " - подходит")
            answer = {'latitude' : records[t_min[0]][6], 'longtitude' : records[t_min[0]][7], 'description' : records[t_min[0]][4]}
            return jsonify(answer)

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")



@app.route('/entrance', methods=['post', 'get'])
def entrance():
    answer = {'phone' : False, 'password' : False, 'output' : "You don't reqistered"}
    if request.method == 'POST':
        db = sqlite3.connect("justUp.db")
        cur = db.cursor()
        req = request.json
        print(req)
        sql = "select phone from users where phone=?"
        cur.execute(sql, [req['phone']])
    if len(cur.fetchall()) == 0:
        return jsonify(answer)
    sql = "select password from users where phone=?"
    cur.execute(sql, [req['phone']])
    if str(req['password']) != str(cur.fetchone()[0]):
        answer['phone'] = True
        answer['output'] = "Wrong password"
        return jsonify(answer)
    answer['password'] = True
    answer['phone'] = True
    answer['output']= "Ok"
    return jsonify(answer)




@app.route("/reg", methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        req = request.form
        print(req)
    conn = sqlite3.connect("justUp.db")
    cursor = conn.cursor()
    select = """select id from users"""
    cursor.execute(select)
    records = cursor.fetchall()
    print("Всего строк:  ", len(records))
    print("Вывод максимума")
    maxi = []
    for row in records:
        maxi.append(row[0])
    cursor.execute(f"INSERT INTO users VALUES ('{max(maxi) + 1}', '{req['fio']}', '{req['phone']}', '{req['email']}', '{req['password']}', '{req['KM']}' )")
    conn.commit()
    cursor.close()
    return 'None'






if __name__ == "__main__":
    app.run(debug=True)
