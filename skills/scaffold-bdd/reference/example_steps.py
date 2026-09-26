"""Example steps: drive the app only through its transports (REST TestClient, gRPC stub). ADAPT names and routes."""

import grpc
from behave import given, then, when

from features.test_helpers import get_current_scenario_context, grpc_channel, rest_client

# ADAPT: generated gRPC modules for the service under test.
# from services.user.v1.proto import user_pb2, user_pb2_grpc


@given('"{email}" is already registered over REST')
def step_already_registered(context, email):
    response = rest_client(context).post("/api/v1/users", json={"email": email})
    assert response.status_code == 201, response.text


@when('I register "{email}" over REST')
def step_register_rest(context, email):
    scenario_context = get_current_scenario_context(context)
    scenario_context.store("response", rest_client(context).post("/api/v1/users", json={"email": email}))


@then("the response status is {status:d}")
def step_response_status(context, status):
    response = get_current_scenario_context(context).get("response")
    assert response.status_code == status, response.text


@then('fetching the user over REST returns email "{email}"')
def step_fetch_rest(context, email):
    user_id = get_current_scenario_context(context).get("response").json()["id"]
    response = rest_client(context).get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200, response.text
    assert response.json()["email"] == email


@when('I register "{email}" over gRPC')
def step_register_grpc(context, email):
    scenario_context = get_current_scenario_context(context)
    stub = user_pb2_grpc.UserServiceStub(grpc_channel(context))
    try:
        scenario_context.store("grpc_reply", stub.Register(user_pb2.RegisterRequest(email=email), timeout=5))
    except grpc.RpcError as e:
        scenario_context.store("grpc_error", e)


@then('the gRPC call succeeds with email "{email}"')
def step_grpc_success(context, email):
    scenario_context = get_current_scenario_context(context)
    error = scenario_context.get("grpc_error")
    assert error is None, f"{error.code()}: {error.details()}"
    assert scenario_context.get("grpc_reply").email == email


# Async servicers: use an `async def` step and `context.app.async_grpc_channel()` inside `async with`.
