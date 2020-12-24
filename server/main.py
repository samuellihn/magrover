import web
import sqlite3
import json
from psycopg2.extensions import adapt, register_adapter, AsIs
import base64


class Database:

    def __init__(self):
        self.connection = sqlite3.connect("magrover.db")
        self.cursor = self.connection.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


class CreateNewRun:
    def POST(self):
        """
        Creates a table of sensor array measurements with the dimensions
        :return: A string with the table name
        """
        database = Database()

        data = json.loads(web.data())
        name = data["name"]
        dimensions = data["dimensions"]

        database.execute(f"""
            CREATE TABLE \"{name}\" (
            time VARCHAR,
            PRIMARY KEY (time)
            );
        """)
        database.commit()

        for x in range(dimensions["x"]):
            for y in range(dimensions["y"]):
                for z in range(dimensions["z"]):
                    for axis in ("x", "y", "z"):
                        database.execute(f"ALTER TABLE \"{name}\" ADD SensorX{x}Y{y}Z{z}Axis{axis} measurement;")
                        database.commit()

        database.close()

        return name


class MeasurementRow:


    def __init__(self, time):
        self.contents = [time]

    def add(self, value):
        self.contents.append(value)

    def __str__(self):
        return str(self.contents).replace("[", "").replace("]", "")



class AppendNewMeasurement:
    def POST(self):
        database = Database()

        table = web.input()["table"]
        data = json.loads(web.data().decode("UTF-8"))
        measurements = data["data"]
        timestamp = data["time"]

        print(measurements)
        row = MeasurementRow(timestamp)
        print(web.input())

        for x in range(len(measurements)):
            for y in range(len(measurements[0])):
                for z in range(len(measurements[0][0])):
                    for axis in ("x", "y", "z"):
                        row.add(measurements[x][y][z][axis])

        database.execute(f"""
            INSERT INTO \"{table}\"  VALUES (
                {str(row)}
            );
        """)
        database.commit()
        database.close()

        return "OK"


class RemoveRun:
    def POST(self):
        """
        Removes a table from the database
        :return: A status message
        """

        database = Database()

        name = json.loads(web.data().decode("UTF-8"))["name"]
        database.cursor.execute(f"""
            DROP TABLE \"{name}\"
        """)
        database.commit()
        database.close()
        return "OK"


urls = (
    "/new/createtable", "CreateNewRun",
    "/new/appendrow", "AppendNewMeasurement",
    "/manage/rmtable", "RemoveRun"
    "/output/rawcsv"
)

app = web.application(urls, globals())


if __name__ == "__main__":
    app.run()