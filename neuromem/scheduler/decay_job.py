"""
NeuraMem Scheduler
APScheduler runner for confidence decay jobs.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from neuromem.core.confidence_decay import get_belief_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecayJob:
    """Scheduled job for confidence decay processing."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Set up scheduled jobs."""
        # Run decay calculation every hour
        self.scheduler.add_job(
            func=self.run_decay_cleanup,
            trigger=IntervalTrigger(hours=1),
            id='confidence_decay',
            name='Run confidence decay cleanup',
            replace_existing=True
        )
        
        # Run full cleanup daily
        self.scheduler.add_job(
            func=self.run_full_cleanup,
            trigger=IntervalTrigger(days=1),
            id='full_cleanup',
            name='Run full belief cleanup',
            replace_existing=True
        )
    
    def run_decay_cleanup(self):
        """Run confidence decay cleanup."""
        logger.info("Running confidence decay cleanup...")
        
        store = get_belief_store()
        expired_ids = store.cleanup_expired(threshold=0.1)
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired beliefs")
        else:
            logger.info("No expired beliefs found")
        
        stats = store.stats()
        logger.info(f"Current belief store stats: {stats}")
    
    def run_full_cleanup(self):
        """Run full system cleanup."""
        logger.info("Running full system cleanup...")
        
        # Clean up beliefs
        self.run_decay_cleanup()
        
        # Additional cleanup tasks can be added here
        logger.info("Full cleanup completed")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler."""
        self.scheduler.shutdown(wait=wait)
        logger.info("Scheduler shutdown")


# Global instance
_decay_job: Optional[DecayJob] = None


def get_scheduler() -> DecayJob:
    """Get the global scheduler instance."""
    global _decay_job
    if _decay_job is None:
        _decay_job = DecayJob()
    return _decay_job


if __name__ == "__main__":
    import time
    
    scheduler = get_scheduler()
    scheduler.start()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
