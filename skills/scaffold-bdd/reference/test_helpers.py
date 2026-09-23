def get_current_scenario_context(context):
    """Return ScenarioContext for the current behave scenario."""
    if not hasattr(context, "scenario_context_pool"):
        raise AttributeError("No scenario context pool available")
    return context.scenario_context_pool.get_context(context.scenario.id)
