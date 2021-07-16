from django.db.models import base
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
# from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import datetime
import sys
from EBookReadingApp.models import DailyUserReadingGoal, UserReadingGoal

# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def manage_goals():
    usergoals = UserReadingGoal.objects.all()
    for i in usergoals:
        todaysgoal = DailyUserReadingGoal(user = i.user, base = i, completedminutes = 0.0)
        todaysgoal.save()
    delete_date = datetime.date.today() - datetime.timedelta(days=60)
    deletinggoals = DailyUserReadingGoal.objects.filter(date = delete_date)
    for i in deletinggoals:
        i.delete()
    


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(manage_goals, 'cron', hour=0, minute = "00", name='clean_accounts', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...")