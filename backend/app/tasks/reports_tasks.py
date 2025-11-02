from app.celery_app import celery_app
from app.db.session import get_engine
from celery.utils.log import get_task_logger
from typing import Optional
import subprocess
import os

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def refresh_materialized(self, view_name: Optional[str]=None, company_id: Optional[str]=None):
    """Refresh materialized views. If view_name is None refresh all known views."""
    engine = get_engine(prefer_read=False)
    views = [
        'mv_gl_ledger_aggregated',
        'mv_account_summary'
    ]
    try:
        with engine.connect() as conn:
            if view_name:
                conn.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name};")
            else:
                for v in views:
                    try:
                        conn.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {v};")
                    except Exception as e:
                        # fallback to non-concurrent
                        logger.warning(f"Concurrent refresh failed for {v}: {e}, trying non-concurrent")
                        conn.execute(f"REFRESH MATERIALIZED VIEW {v};")
        # invalidate relevant cache keys (sync)
        try:
            from app.utils.cache import invalidate_cache_prefix_sync
            # common prefixes used: trial_balance:, ledger:
            invalidate_cache_prefix_sync('trial_balance:')
            invalidate_cache_prefix_sync('ledger:')
        except Exception:
            logger.exception('cache invalidation failed')
        return {'ok': True, 'refreshed': view_name or views}
    except Exception as e:
        logger.exception('refresh failed')
        return {'ok': False, 'error': str(e)}


@celery_app.task(bind=True)
def export_report(self, report_type: str, params: dict, company_id: Optional[str]=None):
    """Long running export job. Creates CSV in uploads/exports and returns path.
    For demo uses a simple CSV dump via psql or Python logic.
    """
    engine = get_engine(prefer_read=True)
    out_dir = os.path.join('uploads','exports')
    os.makedirs(out_dir, exist_ok=True)
    filename = f"export_{report_type}_{company_id or 'all'}_{self.request.id}.csv"
    path = os.path.join(out_dir, filename)
    try:
        # For simplicity, call a Python process to write CSV by calling psql with a COPY if available
        # Here we just create an empty CSV placeholder
        with open(path, 'w') as f:
            f.write('export_type,params\n')
            f.write(f"{report_type},{params}\n")
        return {'ok': True, 'path': path}
    except Exception as e:
        logger.exception('export failed')
        return {'ok': False, 'error': str(e)}
