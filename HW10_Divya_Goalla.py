#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 8 11:00:00 2019

@author: Divya Goalla

    This assignment focuses on adding features to repository created for homework 9 with automated testing.
"""
from collections import defaultdict
import os
from prettytable import PrettyTable
import unittest

class Student:
    """ holds all of the details of a student """

    def __init__(self, cwid, name, major):
        """ student class initializer. """

        self.cwid = cwid 
        self.name = name 
        self.major = major
        self.student_info = defaultdict(str)
        self.student_remaining_courses = []
        self.student_remaining_electives = []
    
    def student_grades(self, course, grade):
        """ add student grades of each course""" 
        
        self.student_info[course] = grade

    def student_add_remaining_courses(self, courses, electives):
        """ add remaining courses to students table""" 
        
        self.student_remaining_courses = courses
        self.student_remaining_electives = electives

    def student_pretty_table(self):
        """ Student Pretty table"""

        return [self.cwid, self.name, self.major, sorted(self.student_info.keys()), self.student_remaining_courses, self.student_remaining_electives]

class Instructor:
    """ holds all of the details of a instructor """

    def __init__(self, cwid, name, dep):
        """ instructor class initializer."""

        self.cwid = cwid 
        self.name = name 
        self.dep = dep
        self.instructor_info = defaultdict(int)
    
    def instructor_courses(self, course):
        """ add student grades of each course""" 
        
        self.instructor_info[course] += 1
    
    def instructor_pretty_table(self):
        """ Instructor Pretty table"""

        return [self.cwid, self.name, self.dep], self.instructor_info

class Repository:
    """ container to hold all of the students, instructor and grading information """

    def __init__(self, directory):
        """ Respository class initializer."""

        self.directory = directory 
        self.student_details = {} 
        self.instructor_details = {}
        self.major_details = defaultdict(lambda : defaultdict(list))
        self.grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        self.analyze_files()
    
    def analyze_files(self):
        """ This method populates the summarized data of student and instructor. """

        dir = os.path.exists(self.directory)
        if not dir:
            print(f"{self.directory} doesn't exist")
            raise FileNotFoundError(f"{self.directory} doesn't exist")
        
        try:
            files = os.listdir(self.directory)
        except FileNotFoundError:
            print(f"Invalid directory {self.directory}")
            raise FileNotFoundError(f"Invalid directory {self.directory}")
        
        if 'students.txt' in files:
            path = os.path.join(self.directory, 'students.txt')
            readfile = list(self.file_reading_gen(path, 3, ';', True))
            for cwid, name, major in readfile:
                self.student_details[cwid] = Student(cwid, name, major)
        
        if 'instructors.txt' in files:
            path = os.path.join(self.directory, 'instructors.txt')
            readfile = list(self.file_reading_gen(path, 3, '|', True))
            for cwid, name, dep in readfile:
                self.instructor_details[cwid] = Instructor(cwid, name, dep)
        
        if 'majors.txt' in files:
            path = os.path.join(self.directory, 'majors.txt')
            readfile = list(self.file_reading_gen(path, 3, '\t', True))
            for major, req_course, course in readfile:
                self.major_details[major][req_course].append(course)
        
        if 'grades.txt' in files:
            path = os.path.join(self.directory, 'grades.txt')
            readfile = list(self.file_reading_gen(path, 4, '|', True))
            for student_cwid, course, grade, instructor_cwid in readfile:
                if student_cwid in self.student_details and grade in self.grades:
                    self.student_details[student_cwid].student_grades(course, grade)
                if instructor_cwid in self.instructor_details:
                    self.instructor_details[instructor_cwid].instructor_courses(course)
        
        for val in self.student_details.values():
            remaining_electives = []
            remaining_courses = []
            for major, req in self.major_details.items():
                if val.major == major:
                    for course in req['E']:
                        if course in val.student_info:
                            remaining_electives = None
                            break

                    for course in req['R']:
                        if not course in val.student_info:
                            remaining_courses.append(course)

                    if remaining_electives is not None or remaining_electives == []:
                        remaining_electives = sorted(req['E'])
                
            self.student_details[val.cwid].student_add_remaining_courses(sorted(remaining_courses), remaining_electives)

    def file_reading_gen(self, path, fields, sep = ",", header = False):
        """ field separated file reader. """

        try:
            fp = open(path, 'r')
        except FileNotFoundError:
            print(f"{path} doesn't exist")
            raise FileNotFoundError(f"{path} doesn't exist")
        else:
            with fp:
                lines = fp.readlines()
                for i in range(len(lines)):
                    if header:
                        header = False
                        continue

                    line_words = lines[i].strip("\n").split(sep)
                    if line_words == ['']:
                        break
                    if fields != len(line_words):
                        print(f"Line {i+1} has blank space/more fields than expected")
                        raise ValueError(f"Line {i+1} has blank space/more fields than expected")
                    yield tuple(line_words)

    def majors_prettytable(self):
        """ Majors summary pretty table """ 

        pt = PrettyTable(field_names = ['Dept', 'Required', 'Electives'])
        for dep, val in self.major_details.items():
            pt.add_row([dep, val['R'], val['E']])
        print(pt)

    def students_prettytable(self):
        """ Student summary pretty table """ 

        pt = PrettyTable(field_names = ['CWID', 'Name', 'Majors', 'Completed Courses', 'Remaining Required', 'Remaining Electives'])
        for student in self.student_details.values():
            pt.add_row(student.student_pretty_table())
        print(pt)
    
    def instructors_prettytable(self):
        """ Instructor summary pretty table """ 

        pt = PrettyTable(field_names = ['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for instructor in self.instructor_details.values():
            instructor_information, courses = instructor.instructor_pretty_table()
            for course, students in courses.items():
                instructor_information.extend([course, students])
                pt.add_row(instructor_information)
                instructor_information = instructor_information[0:3]
        print(pt)


class testcases(unittest.TestCase):
    """ unit tests """

    def test_file_reading_gen_students(self):
        """ verify file reader student"""

        student_res =  [('10103', 'Baldwin, C', 'SFEN'), ('10115', 'Wyatt, X', 'SFEN'), ('10172', 'Forbes, I', 'SFEN'), ('10175', 'Erickson, D', 'SFEN'), ('10183', 'Chapman, O', 'SFEN'), ('11399', 'Cordova, I', 'SYEN'), ('11461', 'Wright, U', 'SYEN'), ('11658', 'Kelly, P', 'SYEN'), ('11714', 'Morton, A', 'SYEN'), ('11788', 'Fuller, E', 'SYEN')] 
    
        univ = Repository(os.getcwd())
        test = list(univ.file_reading_gen('students.txt', 3, ';', True))
        self.assertEqual(test, student_res)
        self.assertNotEqual(list(test),  [('10103', 'Baldwin, C', 'SFEN'), ('10115', 'Wyatt, X', 'SFEN')])

        with self.assertRaises(FileNotFoundError): 
            list(Repository(os.getcwd()).file_reading_gen('abc.txt', 3, '|'))
       
    def test_file_reading_gen_instructors(self):
        """ verify file reader instructor"""

        instructors_res = [('98765', 'Einstein, A', 'SFEN'), ('98764', 'Feynman, R', 'SFEN'), ('98763', 'Newton, I', 'SFEN'), ('98762', 'Hawking, S', 'SYEN'), ('98761', 'Edison, A', 'SYEN'), ('98760', 'Darwin, C', 'SYEN')]

        univ = Repository(os.getcwd())
        test = univ.file_reading_gen('instructors.txt', 3, '|', True )
        self.assertEqual(list(test),  instructors_res)
        self.assertNotEqual(list(test),  [('10103', 'Baldwin, C', 'SFEN'), ('10115', 'Wyatt, X', 'SFEN')])

        with self.assertRaises(FileNotFoundError): 
            list(Repository(os.getcwd()).file_reading_gen('abc.txt', 3, '|'))
        

    def test_file_reading_gen_grades(self):
        """ verify file reader grades """

        grades_res = [('10103', 'SSW 567', 'A', '98765'), ('10103', 'SSW 564', 'A-', '98764'), ('10103', 'SSW 687', 'B', '98764'), ('10103', 'CS 501', 'B', '98764'), ('10115', 'SSW 567', 'A', '98765'), ('10115', 'SSW 564', 'B+', '98764'), ('10115', 'SSW 687', 'A', '98764'), ('10115',
                    'CS 545', 'A', '98764'), ('10172', 'SSW 555', 'A', '98763'), ('10172', 'SSW 567', 'A-', '98765'), ('10175', 'SSW 567', 'A', '98765'), ('10175', 'SSW 564', 'A', '98764'), ('10175', 'SSW 687', 'B-', '98764'), ('10183', 'SSW 689', 'A', '98763'), ('11399', 'SSW 540',
                    'B', '98765'), ('11461', 'SYS 800', 'A', '98760'), ('11461', 'SYS 750', 'A-', '98760'), ('11461', 'SYS 611', 'A', '98760'), ('11658', 'SSW 540', 'F', '98765'), ('11714', 'SYS 611', 'A', '98760'), ('11714', 'SYS 645', 'C', '98760'), ('11788', 'SSW 540', 'A', '98765')]
    
        test = Repository(os.getcwd()).file_reading_gen('grades.txt', 4, '|', True)
        self.assertEqual(list(test),  grades_res)
        self.assertNotEqual(list(test),  [('10103', 'Baldwin, C', 'SFEN'), ('10115', 'Wyatt, X', 'SFEN')])

        with self.assertRaises(FileNotFoundError): 
            list(Repository(os.getcwd()).file_reading_gen('abc.txt', 3, '\t'))
       

    def test_majors_prettytable(self):
        """ verify majors pretty table """

        pt = PrettyTable(field_names = ['Dept', 'Required', 'Electives'])
        pt.add_row(['SFEN', ['SSW 540', 'SSW 564', 'SSW 555', 'SSW 567'], ['CS 501', 'CS 513', 'CS 545']])
        pt.add_row(['SYEN', ['SYS 671', 'SYS 612', 'SYS 800'], ['SSW 810', 'SSW 565', 'SSW 540']])
        self.assertEqual(Repository(os.getcwd()).majors_prettytable(), print(pt))

def main():
    
    try:
        university = Repository(os.getcwd())
        university.majors_prettytable()
        university.students_prettytable()
        university.instructors_prettytable()
    except Exception as e:
        print(f"An expcetion has occurred - {e}")
        raise e
    
if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    main()



