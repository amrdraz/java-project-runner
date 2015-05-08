import csv
from application.models import Student, StudentQuizGrade, StudentMilestoneGrade


def saveOrUpdateQuizGrade(student, quiz, pre, row):
    passed_tests = float(row[pre+" - passed tests"])
    total_tests = float(row[pre+" - total tests"])
    grade_in_percentage = float(row[pre+" - grade %"])
    try:
        grade = StudentQuizGrade.objects.get(student=student, quiz=quiz)
        print "found "+quiz+" grade for "+student.name
    except StudentQuizGrade.DoesNotExist:
        print "new "+quiz+" grade for "+student.name
        grade = StudentQuizGrade(student=student, quiz=quiz)

    grade.passed_tests = passed_tests
    grade.total_tests = total_tests
    grade.grade_in_percentage = grade_in_percentage
    grade.save()
    return grade


def saveOrUpdateMilestoneGrade(student, milestone, pre, row):
    milestone_ratio = float(row[pre+" - ratio (%)"])
    grade_in_percentage = float(row[pre+" - final grade"])
    try:
        grade = StudentMilestoneGrade.objects.get(student=student, milestone=milestone)
        print "found "+milestone+" grade for "+student.name
    except StudentMilestoneGrade.DoesNotExist:
        print "new "+milestone+" grade for "+student.name
        grade = StudentMilestoneGrade(student=student, milestone=milestone)
    grade.milestone_ratio = milestone_ratio
    grade.grade_in_percentage = grade_in_percentage
    grade.save()
    return grade

with open('../401_grades.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        try:
            student = Student.objects.get(guc_id=str(row['GUC ID']))
        except Student.DoesNotExist:
            print str(row['GUC ID']) + "Student does not exist"
            continue

        saveOrUpdateQuizGrade(student, "Quiz 1", "Quiz 1", row)
        saveOrUpdateQuizGrade(student, "Quiz 2", "Quiz 2", row)
        saveOrUpdateQuizGrade(student, "Quiz 3", "Quiz 3", row)
        saveOrUpdateQuizGrade(student, "Quiz 4", "Quiz 4", row)

        saveOrUpdateQuizGrade(student, "Project - Milestone 1 (PRM1)", "PRM1", row)
        saveOrUpdateQuizGrade(student, "Project - Milestone 2 (PRM2)", "PRM2", row)
        saveOrUpdateQuizGrade(student, "Project - Milestone 3 (PRM3)", "PRM3", row)
        saveOrUpdateQuizGrade(student, "Project - Milestone 4 (PRM4)", "PRM4", row)

        saveOrUpdateMilestoneGrade(student, "Milestone 1", "M1", row)
        saveOrUpdateMilestoneGrade(student, "Milestone 2", "M2", row)
        saveOrUpdateMilestoneGrade(student, "Milestone 3", "M3", row)
        saveOrUpdateMilestoneGrade(student, "Milestone 4", "M4", row)

        saveOrUpdateMilestoneGrade(student, "Final Grade", "", row)
