
def project_grades_csv(project_id, suffix=""):
    import csv
    from application.models import Project

    project = Project.objects.get(id=project_id)
    with open(project.name+" "+suffix+' Submissions.csv', 'w') as csvfile:
        fieldnames = [
                'guc_id', 'name', 'email',
                'project', 'passed cases', 'total cases',
                'grade in percentage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in project.student_submissions_for_csv():
            writer.writerow(row)

# example
# project_grades_csv("54f2437d2d1f900e99057d67", "best")
