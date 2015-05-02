import csv
from application.models import Student, StudentQuizGrade, StudentMilestoneGrade


def saveOrUpdateQuizGrade(student, quiz, row):
    try:
        grade = StudentQuizGrade.objects.get(student=student, quiz=quiz)
        print "found quiz grade"
    except StudentQuizGrade.DoesNotExist:
        grade = StudentQuizGrade(student=student, quiz=quiz, passed_tests=float(row["Q1_passed_tests"]), total_tests=float(row["Q1_total_tests"]), grade_in_percentage=float(row["Q1_grade_in_percentage"]))
    grade.save()


def saveOrUpdateMilestoneGrade(student, milestone, row):
    try:
        grade = StudentMilestoneGrade.objects.get(student=student, milestone=milestone)
        print "found milestone grade"
    except StudentMilestoneGrade.DoesNotExist:
        grade = StudentMilestoneGrade(student=student, milestone=milestone, passed_tests=float(row["Q1_passed_tests"]), total_tests=float(row["Q1_total_tests"]), grade_in_percentage=float(row["Q1_grade_in_percentage"]))
    grade.save()

with open('../401_grades.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        student = Student.objects.get(guc_id=str(row['guc_id']))

        saveOrUpdateQuizGrade(student, "Quiz 1", row)
        saveOrUpdateQuizGrade(student, "Quiz 2", row)
        saveOrUpdateQuizGrade(student, "Quiz 3", row)

        saveOrUpdateQuizGrade(student, "Milestone 1", row)
        saveOrUpdateQuizGrade(student, "Milestone 2", row)
        saveOrUpdateQuizGrade(student, "Milestone 3", row)
