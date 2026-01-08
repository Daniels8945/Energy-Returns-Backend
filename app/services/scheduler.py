# # Using APScheduler
# from apscheduler.schedulers.background import BackgroundScheduler

# scheduler = BackgroundScheduler()
# scheduler.add_job(
#     lambda: service.map_zones_with_live_data(session, zones),
#     'cron',
#     hour='*'  # Run every hour
# )
# scheduler.start()


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.feeder_snapshot_job import run_feeder_snapshot

scheduler = BackgroundScheduler(timezone="UTC")

def start_scheduler():
    scheduler.add_job(
        run_feeder_snapshot,
        trigger=CronTrigger(minute=5),  # every hour on the hour
        id="feeder_snapshot_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()