"""
Scheduler — periodically collect models from ALL registered providers.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import get_supabase
from app.collectors import REGISTRY

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def collect_all():
    """Run all registered collectors."""
    supabase = get_supabase()
    for pid, CollectorClass in REGISTRY.items():
        try:
            collector = CollectorClass(supabase)
            count = collector.run()
            logger.info(f"✅ {pid}: {count} models")
        except Exception as e:
            logger.error(f"❌ {pid}: {e}")


def start_scheduler():
    scheduler.add_job(
        collect_all,
        "interval",
        hours=6,
        id="collect_all",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("⏰ Scheduler started — all providers every 6h")


def stop_scheduler():
    scheduler.shutdown(wait=False)
