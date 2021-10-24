from flask import Flask, render_template, url_for, request, jsonify, abort
from geopy.distance import geodesic as GD
import sqlite3
from geopy.geocoders import Nominatim
import geocoder
import re

app = Flask(__name__)



@app.route("/mar", methods=["POST", "GET"])
def sign_in_flask():
    # if request.method == 'POST':

    #     print(req)
    req = request.json
    # conn = sqlite3.connect("/home/fvedenev/JustUpBackFlask/justUp.db")
    # cursor = conn.cursor()


    # cursor.execute(
    #     f"INSERT INTO about_user_history VALUES (1,'{req['transport']}', '{req['climate']}', '{req['type']}','{req['adults']}', '{req['childs']}', '{req['pets']}', '{req['money']}', '{req['dista']}', '{req['distb']}', '{req['date']}', '{req['duration']}')")

    transport = req['transport']
    climate= req['climate']
    type = req['type']
    adults = req['adults']
    childs = req['childs']
    animal = req['pets']
    money = req['money']
    place_A = req['dista']
    place_B = req['distb']
    date = req['date']
    length_days = req['duration']
    geolocator = Nominatim(user_agent="my_request")
    locations = geolocator.geocode(place_A)
    place_A_lat = locations.latitude
    place_A_lon = locations.longitude
    locations = geolocator.geocode(place_B)
    place_B_lat = locations.latitude
    place_B_lon = locations.longitude
    conn = sqlite3.connect("/home/fvedenev/JustUpBackFlask/justUp.db")
    cursor = conn.cursor()
    dataMass = []
    #sql = "SELECT * from travel where transport=? and money between ? and ? and type=? ORDER_BY money DESK"
    sql = "SELECT * from travel where transport=? and money between ? and ?"
    cursor.execute(sql, [transport, 0, (money + 5000)])
    for data in cursor.fetchall():
        if GD((place_A_lat, place_A_lon), (data[1], data[2])).m <= 50000 and GD((place_B_lat, place_B_lon),
                                                                                (data[3], data[4])).m <= 50000:
            dataMass.append(data)

    cursor.execute("INSERT INTO about_user_history VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [transport, climate,
                                                                                                  type, adults, childs,
                                                                                                  animal, money,
                                                                                                  str(place_A), str(place_B),
                                                                                                  date, length_days])
    conn.commit()
    return jsonify(dataMass)
    # conn.commit()
    # return 'None'


@app.route("/near", methods=["POST"])
def near():
    req = request.json
    # if request.method == 'POST':
    #     req = request.json
    #     print(req)
    #g = (57.624758, 39.884910)
    g = (req['latitude'], req['longtitude'])
    #print(g)
    try:
        sqlite_connection = sqlite3.connect('/home/fvedenev/JustUpBackFlask/justUp.db')

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
            answer = {'latitude': records[t_min[0]][6], 'longtitude': records[t_min[0]][7],
                      'description': records[t_min[0]][4]}
            return jsonify(answer)

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


@app.route('/maps/<place>')
def maps(place):
    place = str(place).replace("+", " ")
    geolocator = Nominatim(user_agent="my_request")
    locations = geolocator.geocode(place)
    print(locations)
    print(locations.latitude, locations.longitude)

    return jsonify({"lat": locations.latitude, "lon": locations.longitude})


@app.route('/entrance', methods=['post', 'get'])
def entrance():
    answer = {'phone': False, 'password': False, 'output': "You don't reqistered"}
    db = sqlite3.connect("/home/fvedenev/JustUpBackFlask/justUp.db")
    cur = db.cursor()
    req = request.json
    # if request.method == 'POST':

    #     print(req)
    sql = "select phone from users where phone=?"
    cur.execute(sql, [req['phone']])
    if len(cur.fetchall()) == 0:
        abort(401)
    sql = "select password from users where phone=?"
    cur.execute(sql, [req['phone']])
    if str(req['password']) != str(cur.fetchone()[0]):
        answer['phone'] = True
        answer['output'] = "Wrong password"
        abort(401)
    answer['password'] = True
    answer['phone'] = True
    answer['output'] = "Ok"
    return 'OK'


@app.route("/reg", methods=['POST', 'GET'])
def reg():
    req = request.json
    # if request.method == 'POST':
    #
    #     print(req)
    conn = sqlite3.connect("/home/fvedenev/JustUpBackFlask/justUp.db")
    cursor = conn.cursor()
    select = """select id from users"""
    cursor.execute(select)
    records = cursor.fetchall()
    print("Всего строк:  ", len(records))
    print("Вывод максимума")
    maxi = []
    for row in records:
        maxi.append(row[0])
    cursor.execute(
        f"INSERT INTO users VALUES ('{max(maxi) + 1}', '{req['fio']}', '{req['phone']}', '{req['email']}', '{req['password']}', '{req['KM']}' )")
    conn.commit()
    cursor.close()
    return 'None'


if __name__ == "__main__":
    app.run(debug=True)