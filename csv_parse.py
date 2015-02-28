import csv
import random
from application.models import Student

with open('../game_s15_teams.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        print(row['guc_id'], row['email'])
        email = row['email']
        try:
            student = Student.objects.get(email=email)
            print("found student")
            student.active = True
            student.guc_id = row['guc_id']
            student.team_id = row['team_id']
            student.name = row['name']
            student.tutorial = row['tutorial']
            student.major = row['major']
        except:
            print("did not find student", email)
            student = Student(
                email=email,
                password=random.randrange(100000000, 1000000000),
                active=True,
                guc_id=row['guc_id'],
                team_id=row['team_id'],
                name=row['name'],
                tutorial=row['tutorial'],
                major=row['major'])
        student.save()
        student.reload()
        print(student.to_dict())
