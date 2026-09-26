#!/usr/bin/env bash
# Stage an ArchiPy app with a committed baseline, then add uncommitted and untracked violations for the reviewer.
set -euo pipefail
mkdir -p configs models/errors logics/payment services/payment/v1 repositories/payment
cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["archipy[postgres,fastapi,dependency-injection]>=5.4"]
TOML
touch configs/__init__.py models/__init__.py models/errors/__init__.py logics/__init__.py logics/payment/__init__.py \
  services/__init__.py services/payment/__init__.py services/payment/v1/__init__.py repositories/__init__.py \
  repositories/payment/__init__.py
cat > services/payment/v1/payment_router.py <<'PY'
from fastapi import APIRouter

from logics.payment.payment_logic import PaymentLogic


def create_payment_v1_router(logic: PaymentLogic) -> APIRouter:
    """Build the payment v1 router."""
    router = APIRouter(prefix="/v1/payments")

    @router.post("")
    def charge(amount: int) -> dict[str, str]:
        return {"status": logic.charge(amount)}

    return router
PY
cat > logics/payment/payment_logic.py <<'PY'
class PaymentLogic:
    """Payment use cases."""

    def charge(self, amount: int) -> str:
        """Charge an amount."""
        return "ok"
PY
git init -q
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm "baseline"

# Tracked, uncommitted: unit of work and business rule in the service layer.
cat > services/payment/v1/payment_router.py <<'PY'
from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator
from fastapi import APIRouter

from logics.payment.payment_logic import PaymentLogic


def create_payment_v1_router(logic: PaymentLogic) -> APIRouter:
    """Build the payment v1 router."""
    router = APIRouter(prefix="/v1/payments")

    @router.post("")
    @postgres_sqlalchemy_atomic_decorator
    def charge(amount: int) -> dict[str, str]:
        if amount > 10_000:
            amount = int(amount * 0.95)
        return {"status": logic.charge(amount)}

    return router
PY

# Untracked: adapter in a top-level adapters/ package that leaks raw driver errors and hardcodes a key.
mkdir -p adapters
cat > adapters/payment_gateway.py <<'PY'
import httpx

API_KEY = "sk_live_51Hx9aQeZvKYlo2C"


class PaymentGatewayAdapter:
    """Talks to the payment gateway."""

    def charge(self, amount: int) -> dict:
        response = httpx.post(
            "https://gateway.example.com/charge",
            json={"amount": amount},
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        response.raise_for_status()
        return response.json()
PY
