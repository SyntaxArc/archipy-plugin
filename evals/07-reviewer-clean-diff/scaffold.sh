#!/usr/bin/env bash
# Stage an ArchiPy app with a committed baseline and a clean, rule-conforming uncommitted change.
set -euo pipefail
mkdir -p configs models/dtos/wallet/domain/v1 models/errors logics/wallet logics/notification repositories/wallet
cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["archipy[postgres,fastapi,dependency-injection]>=5.4"]
TOML
touch configs/__init__.py models/__init__.py models/dtos/__init__.py models/errors/__init__.py logics/__init__.py \
  logics/wallet/__init__.py logics/notification/__init__.py models/dtos/wallet/__init__.py \
  models/dtos/wallet/domain/__init__.py models/dtos/wallet/domain/v1/__init__.py repositories/__init__.py \
  repositories/wallet/__init__.py
cat > models/errors/wallet_errors.py <<'PY'
from archipy.models.errors import InsufficientBalanceError as ArchipyInsufficientBalanceError


class InsufficientBalanceError(ArchipyInsufficientBalanceError):
    """Wallet balance is below the requested amount."""
PY
cat > repositories/wallet/wallet_repository.py <<'PY'
from repositories.wallet.adapters.wallet_postgres_adapter import WalletPostgresAdapter


class WalletRepository:
    """Wallet data access."""

    def __init__(self, adapter: WalletPostgresAdapter) -> None:
        """Initialize with the wallet Postgres adapter."""
        self._adapter = adapter

    def get_balance(self, wallet_id: str) -> int:
        """Return the current balance."""
        return self._adapter.get_balance(wallet_id)

    def set_balance(self, wallet_id: str, balance: int) -> int:
        """Persist a new balance and return it."""
        return self._adapter.set_balance(wallet_id, balance)
PY
mkdir -p repositories/wallet/adapters
touch repositories/wallet/adapters/__init__.py
cat > repositories/wallet/adapters/wallet_postgres_adapter.py <<'PY'
from archipy.adapters.postgres.sqlalchemy.adapters import PostgresSQLAlchemyAdapter
from sqlalchemy import text


class WalletPostgresAdapter:
    """Wallet storage on Postgres."""

    def __init__(self, adapter: PostgresSQLAlchemyAdapter) -> None:
        """Initialize with the ArchiPy Postgres adapter."""
        self._adapter = adapter

    def get_balance(self, wallet_id: str) -> int:
        """Read the balance."""
        session = self._adapter.get_session()
        return session.execute(text("SELECT balance FROM wallet WHERE id = :id"), {"id": wallet_id}).scalar_one()

    def set_balance(self, wallet_id: str, balance: int) -> int:
        """Write the balance."""
        session = self._adapter.get_session()
        session.execute(text("UPDATE wallet SET balance = :b WHERE id = :id"), {"b": balance, "id": wallet_id})
        return balance
PY
cat > logics/notification/notification_logic.py <<'PY'
class NotificationLogic:
    """Notification use cases."""

    def notify_low_balance(self, wallet_id: str) -> None:
        """Queue a low-balance notification."""
PY
git init -q
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm "baseline"

cat > models/dtos/wallet/domain/v1/wallet_dtos.py <<'PY'
from archipy.models.dtos.base_dtos import BaseDTO


class WithdrawInputDTO(BaseDTO):
    """Withdraw request."""

    wallet_id: str
    amount: int


class WithdrawOutputDTO(BaseDTO):
    """Withdraw result."""

    balance: int
PY
cat > logics/wallet/wallet_logic.py <<'PY'
from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator

from logics.notification.notification_logic import NotificationLogic
from models.dtos.wallet.domain.v1.wallet_dtos import WithdrawInputDTO, WithdrawOutputDTO
from models.errors.wallet_errors import InsufficientBalanceError
from repositories.wallet.wallet_repository import WalletRepository

LOW_BALANCE_THRESHOLD = 100


class WalletLogic:
    """Wallet use cases."""

    def __init__(self, repository: WalletRepository, notification_logic: NotificationLogic) -> None:
        """Initialize with the wallet repository and notification logic."""
        self._repository = repository
        self._notification_logic = notification_logic

    @postgres_sqlalchemy_atomic_decorator
    def withdraw(self, input_dto: WithdrawInputDTO) -> WithdrawOutputDTO:
        """Withdraw credit, notifying when the balance runs low.

        Raises:
            InsufficientBalanceError: If the wallet balance is below the amount.
        """
        balance = self._repository.get_balance(input_dto.wallet_id)
        if balance < input_dto.amount:
            raise InsufficientBalanceError()
        new_balance = self._repository.set_balance(input_dto.wallet_id, balance - input_dto.amount)
        if new_balance < LOW_BALANCE_THRESHOLD:
            self._notification_logic.notify_low_balance(input_dto.wallet_id)
        return WithdrawOutputDTO(balance=new_balance)
PY
