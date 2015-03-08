import csv
from application.models import Student

with open('data/q1cs.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        student = Student.objects.get(email__iexact=row['GUC Email'])
        student.verification_code = row['Quiz Password code']
        student.save()
        
