import logging
from typing import Any

from beancount.core import data
from sqlmodel import Session, delete

from app.domains.accounts.domain.models import Account
from app.domains.expenses_transactions.domain.models import Expense
from app.domains.income_transactions.domain.models import Income
from app.ledger import Ledger

logger = logging.getLogger(__name__)


class BeancountSyncService:
    def __init__(self, ledger: Ledger, db_session: Session):
        self.ledger = ledger
        self.db = db_session

    def _run_query_and_map(self, query: str, model_cls: type) -> list[Any]:
        """Execute Beancount query and map results to SQLModel instances."""
        res: tuple[list[tuple[str, type]], list[tuple]] = self.ledger.run_query(query)  # type: ignore
        types, rows = res  # type: ignore

        col_names = [col[0] for col in types]
        logger.info(f"Loaded {len(rows)} rows. Columns: {col_names}")  # type: ignore

        mapped = []
        for row in rows:  # type: ignore
            row_dict = {}
            for idx, value in enumerate(row):  # type: ignore
                column_name = col_names[idx]
                if isinstance(value, set | frozenset):
                    row_dict[column_name] = ",".join(sorted(value))  # type: ignore
                else:
                    row_dict[column_name] = value
            mapped.append(model_cls(**row_dict))  # type: ignore
        logger.info(f"Mapped {len(mapped)} rows.")  # type: ignore
        return mapped  # type: ignore

    def sync_table(self, query: str, model_cls: type) -> None:
        """Sync a table by truncating existing data and loading fresh data."""
        self.db.query(model_cls).delete()  # type: ignore
        self.db.commit()
        objects = self._run_query_and_map(query, model_cls)
        self.db.bulk_save_objects(objects)
        self.db.commit()

    def sync_expenses(self) -> None:
        """Sync expenses from Beancount to database."""
        query = """
        SELECT
            date AS date,
            account AS account,
            LEAF(ROOT(account, 2)) as category,
            LEAF(ROOT(account, 3)) as subcategory,
            payee AS payee,
            narration AS narration,
            NUMBER(CONVERT(POSITION, 'ARS', DATE)) AS amount_ars,
            NUMBER(CONVERT(POSITION, 'USD', DATE)) AS amount_usd,
            NUMBER(CONVERT(POSITION, 'CARS', DATE)) AS amount_cars,
            tags
        WHERE account ~ '^Expenses'
        ORDER BY date DESC
        """
        self.sync_table(query, Expense)

    def sync_income(self) -> None:
        """Sync income from Beancount to database."""
        query = """
        SELECT
            date AS date,
            account AS account,
            LEAF(ROOT(account, 3)) AS origin,
            payee AS payee,
            narration AS narration,
            NUMBER(CONVERT(ABS(POSITION), 'ARS', DATE)) AS amount_ars,
            NUMBER(CONVERT(ABS(POSITION), 'USD', DATE)) AS amount_usd,
            NUMBER(CONVERT(ABS(POSITION), 'CARS', DATE)) AS amount_cars
        WHERE account ~ '^Income'
        ORDER BY date DESC
        """
        self.sync_table(query, Income)

    def sync_accounts(self) -> None:
        """Sync accounts from Beancount to database.

        Only syncs accounts that have transactions (either expenses or income).
        """

        def map_account_type(account_type: str) -> str:
            """Map Beancount account types to internal types."""
            if account_type.startswith("Assets:"):
                return "asset"
            elif account_type.startswith("Liabilities:"):
                return "liability"
            elif account_type.startswith("Income:"):
                return "income"
            elif account_type.startswith("Expenses:"):
                return "expense"
            else:
                return "other"

        # First truncate existing accounts
        delete_stmt = delete(Account)
        self.db.exec(delete_stmt)  # type: ignore
        self.db.commit()

        # Get account declarations directly from Beancount entries
        open_directives = [
            entry for entry in self.ledger.entries if isinstance(entry, data.Open)
        ]

        # Get account close directives
        close_directives = {
            entry.account: entry.date
            for entry in self.ledger.entries
            if isinstance(entry, data.Close)
        }

        accounts: list[Account] = []
        for dir in open_directives:
            close_date = close_directives.get(dir.account, None)
            account = Account(
                name=dir.account,
                open_from=dir.date,
                open_to=close_date,
                type=map_account_type(dir.account),
                is_active=True,
            )
            accounts.append(account)

        self.db.add_all(accounts)
        self.db.commit()

        logger.info(f"Synced {len(accounts)} active accounts with transactions.")

    def sync_all(self) -> None:
        """Sync all tables from Beancount to database."""
        try:
            self.sync_accounts()
            self.sync_expenses()
            self.sync_income()
            logger.info("All data synced successfully")
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            raise
