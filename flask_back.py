import re
from geopy.distance import geodesic as GD
import geocoder
from flask import Flask, jsonify
import sqlite3
from geopy.geocoders import Nominatim

app = Flask(__name__)


@app.route('/entrance/phone=<phone>&password=<password>')
def entrance(phone, password):
    db = sqlite3.connect("justUp.db")
    cur = db.cursor()
    sql = "select phone from users where phone=?"
    cur.execute(sql, [phone])
    if len(cur.fetchall()) == 0:
        return jsonify("Данный телефон не зарегистрирован в системе")
    sql = "select password from users where phone=?"
    cur.execute(sql, [phone])
    if str(password) != str(cur.fetchone()[0]):
        return jsonify("Пароль неверный")
    return jsonify("Успешно")


@app.route('/reg/phone=<phone>&fio=<fio>&mail=<mail>&password=<password>')
def reg(phone, fio, mail, password):
    db = sqlite3.connect("justUp.db")
    cur = db.cursor()
    sql = "select phone from users where phone=?"
    cur.execute(sql, [phone])
    if len(cur.fetchall()) != 0:
        return jsonify("Данный телефон уже зарегистрирован в системе")
    if re.fullmatch(r"8\d{10}|\+7\d{10}", str(phone)) is None:
        return jsonify("Неподходящий номер телефона")
    cur.execute("INSERT INTO users (fio, phone, mail, password) VALUES (?, ?, ?, ?)", [fio, phone, mail, password])
    db.commit()
    return jsonify("Успешно зарегистрирован")


@app.route('/maps/<place>')
def maps(place):
    place = str(place).replace("+", " ")
    geolocator = Nominatim(user_agent="my_request")
    locations = geolocator.geocode(place)
    print(locations)
    print(locations.latitude, locations.longitude)

    return jsonify({"lat":locations.latitude, "lon":locations.longitude})


@app.route("/sign_in-flask/transport=<transport>&climate=<climate>&type=<type>&adults=<adults>&childs=<childs>&animal"
           "=<animal>&money=<money>&place_A=<place_A>&place_B=<place_B>&date=<date>&length_days=<length_days>")
def sign_in_flask(transport, climate, type, adults, childs, animal, money, place_A, place_B, date, length_days):
    geolocator = Nominatim(user_agent="my_request")
    locations = geolocator.geocode(place_A)
    place_A_lat = locations.latitude
    place_A_lon = locations.longitude
    locations = geolocator.geocode(place_B)
    place_B_lat = locations.latitude
    place_B_lon = locations.longitude
    conn = sqlite3.connect("justUp.db")
    cursor = conn.cursor()
    dataMass = []
    sql = "SELECT * from travel where transport=? and money between ? and ? and type=? ORDER_BY money DESK"
    for data in cursor.fetchall(sql, [transport, 0, money + 5000, type]):
        if GD((place_A_lat, place_A_lon), (data[1], data[2])).m <= 50000 and GD((place_B_lat, place_B_lon),(data[3], data[4])).m <= 50000:
            dataMass.append(data)

    cursor.execute("INSERT INTO about_user_history VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [transport, climate,
                   type, adults, childs, animal, money, place_A, place_B, date, length_days])
    conn.commit()
    return jsonify(dataMass)


@app.route("/near/coord_lat=<coord_lat>&coord_lon=<coord_lon>")
def near():
    g =geocoder.ip("me").latlng
    try:
        sqlite_connection = sqlite3.connect('justUp.db')

        cursor = sqlite_connection.cursor()

        sqlite_select_query = """SELECT * from places"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        mins = []
        for row in records:
            mins.append(GD(g, (row[6], row[7])))
        mins_num = list(enumerate(mins, 0))

        t_min = min(mins_num, key=lambda i: i[1])
        if GD(g, (records[t_min[0]][6], records[t_min[0]][7])).m <= 1000:
            answer = {'latitude': records[t_min[0]][6], 'longtitude': records[t_min[0]][7],
                      'description': records[t_min[0]][4]}
            return jsonify(answer)

        cursor.close()
        return None
    except sqlite3.Error:
        return None
    finally:
        return None


if __name__ == "__main__":
    app.run(debug=True)
