class Student:
    def __init__(self, name, student_id, grades):
        self.__name = name
        self.__student_id = student_id
        self.__grades = grades  

    
    def get_name(self):
        return self.__name

    def get_student_id(self):
        return self.__student_id

    def get_grades(self):
        return self.__grades

    
    def calculate_average(self):
        if not self.__grades:
            return 0
        return sum(self.__grades) / len(self.__grades)

    def get_grade_category(self):
        avg = self.calculate_average()

        if avg >= 90:
            return "Pass"
        elif avg >= 80:
            return "Pass"
        elif avg >= 70:
            return "Pass"
        elif avg >= 60:
            return "Pass"
        else:
            return "Fail"

    @classmethod
    def from_string(cls, data_str):
        name, student_id, grades_str = data_str.split(",")
        grades = list(map(int, grades_str.split("|")))
        return cls(name, student_id, grades)

    
    @staticmethod
    def is_valid_grade(grade):
        return 0 <= grade <= 100
class Classroom:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def remove_student(self, identifier, by="id"):
        if by == "id":
            self.students = [s for s in self.students if s.get_student_id() != identifier]
        elif by == "name":
            self.students = [s for s in self.students if s.get_name() != identifier]

    def search_student(self, identifier, by="id"):
        for student in self.students:
            if by == "id" and student.get_student_id() == identifier:
                return student
            if by == "name" and student.get_name() == identifier:
                return student
        return None

    def calculate_class_average(self):
        if not self.students:
            return 0

        total = sum(student.calculate_average() for student in self.students)
        return total / len(self.students)
