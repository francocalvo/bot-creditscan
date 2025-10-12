"""
Load the ledger file and store the entries, errors, and options.
"""

from beancount.core.data import BeancountError, Directive
from beancount.loader import load_file
from beanquery.query import run_query


class Ledger:
    """
    Returns the entries, errors, and options from the ledger file.
    """

    entries: list[Directive]
    errors: list[BeancountError]
    options: dict[str, str]

    def __init__(self, ledger_path: str) -> None:
        """
        Load the ledger file and store the entries, errors, and options.
        """
        self.path = ledger_path
        entries, errors, options = load_file(self.path)

        self.entries = entries
        self.errors = errors
        self.options = options

    def run_query(
        self, query: str
    ) -> tuple[list[tuple[str, type]], list[dict[str, type]]]:
        """
        Run the query on the entries and return the result.
        """
        return run_query(self.entries, self.options, query) # type: ignore[no-untyped-call]

    def __hash__(self) -> int:
        """
        Return the hash of the ledger file.
        """
        return hash(frozenset([frozenset(str(entr) for entr in self.entries)]))


def ledger_hash(ledger: Ledger) -> int:
    """
    Return the hash of the ledger file.
    """
    return hash(frozenset(str(entr) for entr in ledger.entries))
