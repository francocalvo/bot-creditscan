"""Unit tests for tag rule engine evaluation logic."""

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlmodel import Session

from app.domains.card_statements.domain.models import CardStatement
from app.domains.credit_cards.domain.models import CardBrand, CreditCard
from app.domains.tag_rules.domain.models import TagRuleCreate
from app.domains.tag_rules.repository import TagRuleRepository
from app.domains.tag_rules.service import TagRuleService
from app.domains.tags.domain.models import Tag
from app.domains.tags.repository import TagRepository
from app.domains.transaction_tags.repository import TransactionTagRepository
from app.domains.transactions.domain.models import Transaction
from app.models import User


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """Test user ID."""
    return uuid.uuid4()


@pytest.fixture
def test_user_id_2() -> uuid.UUID:
    """Test user ID 2."""
    return uuid.uuid4()


@pytest.fixture
def db_session() -> Session:
    """Create a test database session."""
    # Import here to avoid issues with test isolation
    from sqlmodel import create_engine
    from sqlmodel.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def user(db_session: Session) -> User:
    """Create a test user."""
    from app.models import User

    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user2(db_session: Session) -> User:
    """Create a second test user."""
    from app.models import User

    user2 = User(
        email="test2@example.com",
        hashed_password="hashed",
        full_name="Test User 2",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    return user2


@pytest.fixture
def credit_card(db_session: Session, user: User) -> CreditCard:
    """Create a test credit card."""
    card = CreditCard(
        user_id=user.id,
        bank="Test Bank",
        brand=CardBrand.VISA,
        last4="1234",
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card


@pytest.fixture
def card_statement(db_session: Session, credit_card: CreditCard) -> CardStatement:
    """Create a test card statement."""
    statement = CardStatement(
        card_id=credit_card.id,
        period_start=datetime(2026, 1, 1).date(),
        period_end=datetime(2026, 1, 31).date(),
        close_date=datetime(2026, 1, 25).date(),
        due_date=datetime(2026, 2, 15).date(),
        previous_balance=Decimal("0.00"),
        current_balance=Decimal("100.00"),
        minimum_payment=Decimal("25.00"),
        is_fully_paid=False,
    )
    db_session.add(statement)
    db_session.commit()
    db_session.refresh(statement)
    return statement


@pytest.fixture
def transaction(db_session: Session, card_statement: CardStatement) -> Transaction:
    """Create a test transaction."""
    txn = Transaction(
        statement_id=card_statement.id,
        txn_date=datetime(2026, 1, 15).date(),
        payee="Amazon",
        description="Online purchase",
        amount=Decimal("50.00"),
        currency="USD",
    )
    db_session.add(txn)
    db_session.commit()
    db_session.refresh(txn)
    return txn


@pytest.fixture
def tag(db_session: Session, user: User) -> Tag:
    """Create a test tag."""
    tag = Tag(
        user_id=user.id,
        label="Shopping",
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture
def tag_service(db_session: Session) -> TagRepository:
    """Create tag service."""
    return TagRepository(db_session)


@pytest.fixture
def tag_rule_service(db_session: Session) -> TagRuleService:
    """Create tag rule service."""
    return TagRuleService(
        tag_rule_repository=TagRuleRepository(db_session),
        tag_repository=TagRepository(db_session),
        transaction_tag_repository=TransactionTagRepository(db_session),
    )


class TestRuleEvaluation:
    """Test rule evaluation logic."""

    def test_payee_contains_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that payee_contains matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            name="Amazon purchases",
            payee_contains="amazon",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_payee_contains_case_insensitive(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that payee_contains is case-insensitive."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_contains="AMAZON",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_payee_contains_no_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that payee_contains doesn't match when substring not found."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_contains="Netflix",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is False
        )

    def test_description_contains_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that description_contains matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            description_contains="online",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_description_regex_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that description_regex matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            description_regex=r"on.*purchase",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_payee_regex_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that payee_regex matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_regex=r"^ama.*n$",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_amount_min_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that amount_min matches correctly (inclusive)."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            amount_min=Decimal("40.00"),
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_amount_min_no_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that amount_min doesn't match when amount is too low."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            amount_min=Decimal("60.00"),
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is False
        )

    def test_amount_max_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that amount_max matches correctly (inclusive)."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            amount_max=Decimal("60.00"),
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_amount_max_no_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that amount_max doesn't match when amount is too high."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            amount_max=Decimal("40.00"),
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is False
        )

    def test_amount_range_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that amount range matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            amount_min=Decimal("40.00"),
            amount_max=Decimal("60.00"),
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_currency_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that currency matches correctly."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            currency="USD",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_currency_case_insensitive(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that currency is case-insensitive."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            currency="usd",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_currency_no_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that currency doesn't match when different."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            currency="EUR",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is False
        )

    def test_and_semantics_all_match(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that all conditions must match (AND semantics)."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_contains="amazon",
            amount_min=Decimal("40.00"),
            currency="USD",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is True
        )

    def test_and_semantics_one_fails(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        transaction: Transaction,
    ) -> None:
        """Test that if one condition fails, the rule doesn't match."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_contains="amazon",
            amount_min=Decimal("60.00"),  # This will fail (50 < 60)
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user.id) is False
        )

    def test_ownership_check_different_user(
        self,
        tag_rule_service: TagRuleService,
        tag: Tag,
        user: User,
        user2: User,
        transaction: Transaction,
    ) -> None:
        """Test that transactions from a different user don't match."""
        rule = TagRuleCreate(
            user_id=user2.id,  # User 2's rule
            tag_id=tag.tag_id,
            payee_contains="amazon",
        )
        created_rule = tag_rule_service.tag_rule_repository.create(rule)

        # Transaction belongs to user, rule belongs to user2
        assert (
            tag_rule_service._evaluate_rule(created_rule, transaction, user2.id)
            is False
        )


class TestRuleCreation:
    """Test rule creation and validation."""

    def test_rule_creation_with_at_least_one_condition(
        self, tag_rule_service: TagRuleService, tag: Tag, user: User
    ) -> None:
        """Test that rule with at least one condition can be created."""
        rule = TagRuleCreate(
            user_id=user.id,
            tag_id=tag.tag_id,
            payee_contains="amazon",
        )
        created_rule = tag_rule_service.create_tag_rule(rule)

        assert created_rule.tag_id == tag.tag_id
        assert created_rule.user_id == user.id

    def test_rule_creation_no_conditions_fails(
        self, tag_rule_service: TagRuleService, tag: Tag, user: User
    ) -> None:
        """Test that rule with no conditions fails."""
        with pytest.raises(
            ValidationError, match="At least one match condition must be set"
        ):
            TagRuleCreate(
                user_id=user.id,
                tag_id=tag.tag_id,
            )

    def test_rule_creation_invalid_regex_fails(
        self, tag_rule_service: TagRuleService, tag: Tag, user: User
    ) -> None:
        """Test that rule with invalid regex fails."""
        with pytest.raises(ValidationError, match="Invalid regex pattern"):
            TagRuleCreate(
                user_id=user.id,
                tag_id=tag.tag_id,
                payee_regex="[invalid(",  # Invalid regex
            )

    def test_rule_creation_wrong_user_fails(
        self, tag_rule_service: TagRuleService, tag: Tag, user: User, user2: User
    ) -> None:
        """Test that rule creation fails when tag belongs to different user."""
        rule = TagRuleCreate(
            user_id=user2.id,  # Different user
            tag_id=tag.tag_id,  # Tag belongs to user
            payee_contains="amazon",
        )

        from app.domains.tag_rules.domain.errors import TagRuleOwnershipError

        with pytest.raises(TagRuleOwnershipError):
            tag_rule_service.create_tag_rule(rule)
