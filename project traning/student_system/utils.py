import csv
from models import Student


def load_students(filename):
    students = []

    try:
        with open(filename, newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                name, student_id, *grades = row
                grades = list(map(int, grades))
                students.append(Student(name, student_id, grades))

    except FileNotFoundError:
        print("File not found.")

    return students


def save_students(filename, classroom):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        for student in classroom.students:
            writer.writerow([
                student.get_name(),
                student.get_student_id(),
                *student.get_grades()
            ])
