
def project_grades_csv(project_id):
    import csv
    from application.models import Project

    project = Project.objects.get(id=project_id)
    with open(project.name+' Grades.csv', 'w') as csvfile:
        fieldnames = [
                'team_id', 'guc_id', 'name', 'email',
                'project', 'passed cases', 'total cases',
                'grade in percentage', 'submitter']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in project.student_results_for_csv():
            writer.writerow(row)

# example
# project_grades_csv("54f2437d2d1f900e99057d67")
