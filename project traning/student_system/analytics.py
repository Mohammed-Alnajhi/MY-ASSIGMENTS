def top_student(classroom):
    return max(classroom.students, key=lambda s: s.calculate_average(), default=None)


def lowest_student(classroom):
    return min(classroom.students, key=lambda s: s.calculate_average(), default=None)


def rank_students(classroom):
    return sorted(
        classroom.students,
        key=lambda s: s.calculate_average(),
        reverse=True
    )


def grade_distribution(classroom):
    distribution = {}

    for student in classroom.students:
        grade = student.get_grade_category()
        distribution[grade] = distribution.get(grade, 0) + 1

    return distribution
