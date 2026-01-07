# Using APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: service.map_zones_with_live_data(session, zones),
    'cron',
    hour='*'  # Run every hour
)
scheduler.start()