import logging
from pathlib import Path

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.services.beancount.sync import BeancountSyncService

logger = logging.getLogger(__name__)

FILE_PATTERNS = {".bean", ".beancount"}


class LedgerChangeHandler(FileSystemEventHandler):
    """Handler for Beancount ledger file changes."""

    def __init__(
        self,
        sync_service: BeancountSyncService,
    ):
        self.sync_service = sync_service
        self.file_patterns: set[str] = FILE_PATTERNS
        self._last_sync_path = None

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        """Handle file modification events."""
        if (
            not event.is_directory
            and isinstance(event.src_path, str)
            and Path(event.src_path).suffix in self.file_patterns
        ):
            # Avoid duplicate syncs for the same file
            if event.src_path == self._last_sync_path:
                return

            self._last_sync_path = event.src_path
            logger.info(f"Detected changes in {event.src_path}, syncing data...")

            try:
                self.sync_service.sync_all()
                logger.info("Data sync completed successfully")
            except Exception as e:
                logger.error(f"Error syncing data: {str(e)}")


class LedgerWatcher:
    """Watches Beancount ledger files for changes."""

    def __init__(self, path: str, sync_service: BeancountSyncService):
        self.path = path
        self.sync_service = sync_service
        self.observer = None

    def start(self) -> None:
        """Start watching the ledger directory."""
        if self.observer:
            return

        try:
            handler = LedgerChangeHandler(self.sync_service)
            self.observer = Observer()
            self.observer.schedule(handler, self.path, recursive=False)
            self.observer.start()
            logger.info(f"Started watching for changes in {self.path}")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {str(e)}")
            raise

    def stop(self) -> None:
        """Stop watching the ledger directory."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Stopped watching for changes")
