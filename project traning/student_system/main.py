from models import Student, Classroom
from analytics import *
from utils import *

def main():
    classroom = Classroom()

    students = load_students("data.csv")
    for student in students:
        classroom.add_student(student)

    while True:
        print("\n1. Add Student")
        print("2. Show Top Student")
        print("3. Show Lowest Student")
        print("4. Show Ranking")
        print("5. Search Student")
        print("6. Remove Student")
        print("7. Exit")

        choice = input("Choose option: ")

        try:
            if choice == "1":
                name = input("Name: ")
                student_id = input("ID: ")

                if classroom.search_student(student_id) is not None:
                    print("ID already exists. Please use a diffrent ID.")
                    continue

                grades = []
                for i in range(3):
                    grade = int(input(f"Grade {i+1}: "))
                    if Student.is_valid_grade(grade):
                        grades.append(grade)
                    else:
                        raise ValueError("Invalid grade")

                student = Student(name, student_id, grades)
                classroom.add_student(student)

            elif choice == "2":
                student = top_student(classroom)
                if student:
                    avg = student.calculate_average()
                    status = "Pass" if avg >= 60 else "Fail"
                    print("Top student:")
                    print(student.get_student_id(), student.get_name(), round(avg,2), status)

            elif choice == "3":
                student = lowest_student(classroom)
                if student:
                    avg = student.calculate_average()
                    status = "Pass" if avg >= 60 else "Fail"
                    print("Low student:")
                    print(student.get_student_id(), student.get_name(), round(avg,2), status)

            elif choice == "4":
                ranking = rank_students(classroom)
                for s in ranking:
                    avg = s.calculate_average()
                    status = "Pass" if avg >= 60 else "Fail"
                    print(s.get_student_id(), s.get_name(), round(avg,2), status)
            elif choice == "5":
                print("Search by: 1-ID  or  2-Name")
                mode = input("Choose (1/2): ")
                if mode == "1":
                    sid = input("ID: ")
                    s = classroom.search_student(sid, by="id")
                else:
                    name_q = input("Name: ")
                    s = classroom.search_student(name_q, by="name")

                if s:
                    avg = s.calculate_average()
                    status = "Pass" if avg >= 60 else "Fail"
                    print(s.get_student_id(), s.get_name(), round(avg,2), status)
                else:
                    print("Student not found.")

            elif choice == "6":
                print("Remove by: 1-ID  2-Name")
                mode = input("Choose (1/2): ")
                if mode == "1":
                    sid = input("ID to remove: ")
                    s = classroom.search_student(sid, by="id")
                    if s:
                        classroom.remove_student(sid, by="id")
                        print("Removed:", sid, s.get_name())
                    else:
                        print("Student not found.")
                else:
                    name_r = input("Name to remove: ")
                    matches = [st for st in classroom.students if st.get_name() == name_r]
                    if not matches:
                        print("Student not found.")
                    else:
                        count = len(matches)
                        classroom.remove(name_r, by="name")
                        print(f"Removed {count} student(s) with name '{name_r}'.")

            elif choice == "7":
                save_students("data.csv", classroom)
                break

        except ValueError as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
