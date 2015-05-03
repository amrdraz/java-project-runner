import csv
from application.models import Student, StudentQuizGrade, StudentMilestoneGrade


def saveOrUpdateQuizGrade(student, quiz, pre, row):
    try:
        grade = StudentQuizGrade.objects.get(student=student, quiz=quiz)
        print "found quiz grade"
    except StudentQuizGrade.DoesNotExist:
        grade = StudentQuizGrade(student=student, quiz=quiz, passed_tests=float(row[pre+"_passed_tests"]), total_tests=float(row[pre+"_total_tests"]), grade_in_percentage=float(row[pre+"_grade_in_percentage"]))
    grade.save()


def saveOrUpdateMilestoneGrade(student, milestone, pre, row):
    try:
        grade = StudentMilestoneGrade.objects.get(student=student, milestone=milestone)
        print "found milestone grade"
    except StudentMilestoneGrade.DoesNotExist:
        grade = StudentMilestoneGrade(student=student, milestone=milestone, milestone_ratio=[pre+"_ratio"], grade_in_percentage=float(row[pre+"_final_grade_in_percentage"]))
    grade.save()

with open('../401_grades.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        student = Student.objects.get(guc_id=str(row['guc_id']))

        saveOrUpdateQuizGrade(student, "Quiz 1", "Q1", row)
        saveOrUpdateQuizGrade(student, "Quiz 2", "Q2", row)
        saveOrUpdateQuizGrade(student, "Quiz 3", "Q3", row)

        saveOrUpdateMilestoneGrade(student, "Milestone 1", "M1", row)
        saveOrUpdateMilestoneGrade(student, "Milestone 2", "M2", row)
        saveOrUpdateMilestoneGrade(student, "Milestone 3", "M3", row)
