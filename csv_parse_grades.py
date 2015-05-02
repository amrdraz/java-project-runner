import csv
from application.models import Student, StudentQuizGrade, StudentMilestoneGrade

with open('../401_grades.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        student = Student.objects.get(guc_id=row['guc_id'])
        StudentQuizGrade(student=student, quiz="Quiz 1", passed_tests=float(row["Q1_passed_tests"]), total_tests=float(row["Q1_total_tests"]), grade_in_percentage=float(row["Q1_grade_in_percentage"])).save()
        StudentQuizGrade(student=student, quiz="Quiz 2", passed_tests=float(row["Q2_passed_tests"]), total_tests=float(row["Q2_total_tests"]), grade_in_percentage=float(row["Q2_grade_in_percentage"])).save()
        StudentQuizGrade(student=student, quiz="Quiz 3", passed_tests=float(row["Q3_passed_tests"]), total_tests=float(row["Q3_total_tests"]), grade_in_percentage=float(row["Q3_grade_in_percentage"])).save()

        StudentMilestoneGrade(student=student, milestone="Milestone 1", milestone_ratio=float(row["M1_ratio"]), grade_in_percentage=float(row['M1_final_grade_in_percentage'])).save()
        StudentMilestoneGrade(student=student, milestone="Milestone 2", milestone_ratio=float(row["M2_ratio"]), grade_in_percentage=float(row['M2_final_grade_in_percentage'])).save()
        StudentMilestoneGrade(student=student, milestone="Milestone 3", milestone_ratio=float(row["M3_ratio"]), grade_in_percentage=float(row['M3_final_grade_in_percentage'])).save()
