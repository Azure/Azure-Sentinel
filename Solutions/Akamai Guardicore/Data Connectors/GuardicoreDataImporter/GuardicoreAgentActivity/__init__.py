from .models.agent import GuardicoreAgent
from ..utils.import_logic import run_import_loop

async def main(name: str):
    return await run_import_loop(
        destination_table='GuardicoreAgents',
        api_endpoint='api/v3.0/agents',
        method='GET',
        params={},
        model_class=GuardicoreAgent,
        add_sampling_timestamp=True,
    )