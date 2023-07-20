from apscheduler.schedulers.background import BackgroundScheduler
from jobs.tasks import delete_inactive_users

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_inactive_users, 'interval', minutes=60)
    scheduler.start()
