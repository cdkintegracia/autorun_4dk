from datetime import datetime, timedelta

job_start_time = datetime.now()
job_maximum_time = datetime.now() + timedelta(hours=2)
print(job_start_time)
print(job_maximum_time)