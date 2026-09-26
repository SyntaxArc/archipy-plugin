def get_current_scenario_context(context):
    """Return ScenarioContext for the current behave scenario."""
    if not hasattr(context, "scenario_context_pool"):
        raise AttributeError("No scenario context pool available")
    return context.scenario_context_pool.get_context(context.scenario.id)


def rest_client(context):
    """FastAPI TestClient bound to the real app (AppUtils handlers, middleware, lifespan)."""
    if context.app.rest is None:
        raise RuntimeError("App has no REST API; implement build_rest_app() in features/app_harness.py")
    return context.app.rest


def grpc_channel(context):
    """Sync gRPC channel to the real app server; build generated stubs from it."""
    return context.app.grpc_channel()
