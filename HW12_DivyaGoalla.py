# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 11:52:13 2019

@author: Kavya
"""
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
db_path = "C:/SQLite/SSW.db"

@app.route('/instructors')
def get_instructors():

    try:
        db = sqlite3.connect(db_path)
    except Exception as e:
        return render_template('error.html', error_message = e)
    else:
        query = "select a.CWID, a.Name, a.Dept, b.Course, count(b.Course) as num_of_students from instructors as a "
        query += "join grades as b on a.CWID = b.InstructorCWID "
        query += "group by a.CWID, a.Name, a.Dept, b.Course "
        query += "order by a.CWID asc"
        try:
            result = db.execute(query)
        except Exception as e:
            return render_template('error.html', error_message = e)
        else:
            instructor_arr = []
            for row in result:
                instructor_arr.append({'cwid' : row[0], 'name' : row[1], 'department' : row[2], 'course' : row[3], 'students' : row[4]})
            db.close()
            return render_template('instructor.html',header = "Instructor Repository", table_title = "Instructor details" ,data = instructor_arr)


if __name__ == "__main__":
  app.run()