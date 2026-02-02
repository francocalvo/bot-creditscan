"""Tag rule service implementation."""

import re
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import select

from app.domains.card_statements.domain.models import CardStatement
from app.domains.credit_cards.domain.models import CreditCard
from app.domains.tag_rules.domain.errors import TagRuleOwnershipError
from app.domains.tag_rules.domain.models import (
    ApplyRulesRequest,
    ApplyRulesResponse,
    TagRule,
    TagRuleCreate,
    TagRulePublic,
    TagRulesPublic,
    TagRuleUpdate,
)
from app.domains.tag_rules.repository import TagRuleRepository, provide_tag_rule_repository
from app.domains.tags.repository import TagRepository, provide as provide_tag_repository
from app.domains.transaction_tags.domain.errors import TransactionTagNotFoundError
from app.domains.transaction_tags.repository import (
    TransactionTagRepository,
    provide as provide_transaction_tag_repository,
)
from app.domains.transactions.domain.models import Transaction


class TagRuleService:
    """Service for tag rules."""

    def __init__(
        self,
        tag_rule_repository: TagRuleRepository,
        tag_repository: TagRepository,
        transaction_tag_repository: TransactionTagRepository,
    ):
        """Initialize the service with repositories."""
        self.tag_rule_repository = tag_rule_repository
        self.tag_repository = tag_repository
        self.transaction_tag_repository = transaction_tag_repository

    def create_tag_rule(self, rule_data: TagRuleCreate) -> TagRulePublic:
        """Create a new tag rule."""
        # Verify that tag belongs to the same user
        tag = self.tag_repository.get_by_id(rule_data.tag_id)
        if tag.user_id != rule_data.user_id:
            raise TagRuleOwnershipError(
                f"Tag {rule_data.tag_id} does not belong to user {rule_data.user_id}"
            )

        rule = self.tag_rule_repository.create(rule_data)
        return TagRulePublic.model_validate(rule)

    def get_tag_rule(self, rule_id: uuid.UUID) -> TagRulePublic:
        """Get a tag rule by ID."""
        rule = self.tag_rule_repository.get_by_id(rule_id)
        return TagRulePublic.model_validate(rule)

    def list_tag_rules(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> TagRulesPublic:
        """List tag rules with pagination and filtering."""
        rules = self.tag_rule_repository.list(skip=skip, limit=limit, filters=filters)
        count = self.tag_rule_repository.count(filters=filters)

        return TagRulesPublic(
            data=[TagRulePublic.model_validate(r) for r in rules],
            count=count,
        )

    def update_tag_rule(
        self, rule_id: uuid.UUID, rule_data: TagRuleUpdate
    ) -> TagRulePublic:
        """Update a tag rule."""
        # Get existing rule to check ownership
        existing_rule = self.tag_rule_repository.get_by_id(rule_id)

        # If tag_id is being updated, verify ownership
        if rule_data.tag_id is not None:
            tag = self.tag_repository.get_by_id(rule_data.tag_id)
            if tag.user_id != existing_rule.user_id:
                raise TagRuleOwnershipError(
                    f"Tag {rule_data.tag_id} does not belong to user {existing_rule.user_id}"
                )

        # Update the rule (repository will handle the update)
        rule = self.tag_rule_repository.update(rule_id, rule_data)

        # Manually update the updated_at timestamp
        rule.updated_at = datetime.utcnow()
        self.tag_rule_repository.db_session.add(rule)
        self.tag_rule_repository.db_session.commit()
        self.tag_rule_repository.db_session.refresh(rule)

        return TagRulePublic.model_validate(rule)

    def delete_tag_rule(self, rule_id: uuid.UUID) -> None:
        """Delete a tag rule."""
        self.tag_rule_repository.delete(rule_id)

    def _evaluate_rule(
        self, rule: TagRule, transaction: Transaction, user_id: uuid.UUID
    ) -> bool:
        """Evaluate if a transaction matches a rule."""
        # Verify ownership: transaction must belong to rule's user
        if not self._transaction_belongs_to_user(transaction, user_id):
            return False

        # Check payee_contains (case-insensitive)
        if rule.payee_contains:
            if rule.payee_contains.lower() not in transaction.payee.lower():
                return False

        # Check description_contains (case-insensitive)
        if rule.description_contains:
            if rule.description_contains.lower() not in transaction.description.lower():
                return False

        # Check payee_regex
        if rule.payee_regex:
            try:
                pattern = re.compile(rule.payee_regex, re.IGNORECASE)
                if not pattern.search(transaction.payee):
                    return False
            except re.error:
                # Invalid regex should have been caught at creation/update
                return False

        # Check description_regex
        if rule.description_regex:
            try:
                pattern = re.compile(rule.description_regex, re.IGNORECASE)
                if not pattern.search(transaction.description):
                    return False
            except re.error:
                # Invalid regex should have been caught at creation/update
                return False

        # Check amount_min (inclusive) - skip if amount is NULL
        if rule.amount_min is not None:
            if transaction.amount is None:
                return False
            if transaction.amount < rule.amount_min:
                return False

        # Check amount_max (inclusive) - skip if amount is NULL
        if rule.amount_max is not None:
            if transaction.amount is None:
                return False
            if transaction.amount > rule.amount_max:
                return False

        # Check currency (exact match, case-insensitive)
        if rule.currency:
            if transaction.currency.upper() != rule.currency.upper():
                return False

        # All checks passed
        return True

    def _transaction_belongs_to_user(
        self, transaction: Transaction, user_id: uuid.UUID
    ) -> bool:
        """Check if a transaction belongs to a user via statement->card->user chain."""
        db_session = self.tag_rule_repository.db_session

        # Join: transaction -> card_statement -> credit_card
        query = (
            select(CreditCard)
            .join(CardStatement, CreditCard.id == CardStatement.card_id)
            .where(
                CardStatement.id == transaction.statement_id,
                CreditCard.user_id == user_id,
            )
        )

        result = db_session.exec(query).first()
        return result is not None

    def _apply_tag_to_transaction(
        self, transaction_id: uuid.UUID, tag_id: uuid.UUID
    ) -> bool:
        """Apply a tag to a transaction (idempotent). Returns True if newly applied."""
        # Check if already tagged
        try:
            self.transaction_tag_repository.get_by_ids(transaction_id, tag_id)
            # Already exists, nothing to do
            return False
        except TransactionTagNotFoundError:
            # Doesn't exist, create it
            from app.domains.transaction_tags.domain.models import TransactionTagCreate

            self.transaction_tag_repository.create(
                TransactionTagCreate(transaction_id=transaction_id, tag_id=tag_id)
            )
            return True

    def apply_rules_to_transaction(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID, dry_run: bool = False
    ) -> dict[str, Any]:
        """Apply applicable rules to a single transaction."""
        # Get the transaction
        db_session = self.tag_rule_repository.db_session
        transaction = db_session.get(Transaction, transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")

        # Get applicable rules for the user
        rules = self.tag_rule_repository.list_applicable_for_user(
            user_id, enabled_only=True
        )

        applied_tags = []
        evaluated_count = 1

        for rule in rules:
            if self._evaluate_rule(rule, transaction, user_id):
                if not dry_run:
                    newly_applied = self._apply_tag_to_transaction(
                        transaction.id, rule.tag_id
                    )
                    if newly_applied:
                        applied_tags.append(str(rule.tag_id))
                else:
                    # Dry run: just record what would be applied
                    # Check if already tagged
                    try:
                        self.transaction_tag_repository.get_by_ids(
                            transaction.id, rule.tag_id
                        )
                    except Exception:
                        applied_tags.append(str(rule.tag_id))

        return {
            "evaluated_count": evaluated_count,
            "applied_count": len(applied_tags),
            "transaction_id": str(transaction_id),
            "applied_tag_ids": applied_tags,
        }

    def apply_rules(
        self,
        user_id: uuid.UUID,
        request: ApplyRulesRequest,
    ) -> ApplyRulesResponse:
        """Apply rules to transactions based on filters."""
        db_session = self.tag_rule_repository.db_session

        # Build query for transactions with ownership filter
        # Join: transaction -> card_statement -> credit_card to enforce ownership
        query = (
            select(Transaction)
            .join(CardStatement, Transaction.statement_id == CardStatement.id)
            .join(CreditCard, CardStatement.card_id == CreditCard.id)
            .where(CreditCard.user_id == user_id)
        )

        # Apply filters
        if request.transaction_id:
            query = query.where(Transaction.id == request.transaction_id)
        elif request.statement_id:
            query = query.where(Transaction.statement_id == request.statement_id)

        # Date filters (if provided)
        if request.date_from:
            query = query.where(Transaction.txn_date >= request.date_from.date())
        if request.date_to:
            query = query.where(Transaction.txn_date <= request.date_to.date())

        # Get transactions
        transactions = db_session.exec(query).all()

        # Get applicable rules for the user
        rules = self.tag_rule_repository.list_applicable_for_user(
            user_id, enabled_only=True
        )

        evaluated_count = len(transactions)
        applied_count = 0
        details = []

        # Evaluate each transaction against each rule
        for transaction in transactions:
            for rule in rules:
                if self._evaluate_rule(rule, transaction, user_id):
                    # Check if already tagged (for dry run counting)
                    try:
                        self.transaction_tag_repository.get_by_ids(
                            transaction.id, rule.tag_id
                        )
                        already_tagged = True
                    except TransactionTagNotFoundError:
                        already_tagged = False

                    if not already_tagged:
                        if not request.dry_run:
                            self._apply_tag_to_transaction(transaction.id, rule.tag_id)
                            applied_count += 1
                        else:
                            applied_count += 1

                        if request.dry_run:
                            details.append(
                                {
                                    "transaction_id": str(transaction.id),
                                    "tag_id": str(rule.tag_id),
                                    "rule_id": str(rule.id),
                                }
                            )

        return ApplyRulesResponse(
            evaluated_count=evaluated_count,
            applied_count=applied_count,
            details=details if request.dry_run else None,
        )


def provide() -> TagRuleService:
    """Provide an instance of TagRuleService."""
    return TagRuleService(
        tag_rule_repository=provide_tag_rule_repository(),
        tag_repository=provide_tag_repository(),
        transaction_tag_repository=provide_transaction_tag_repository(),
    )
