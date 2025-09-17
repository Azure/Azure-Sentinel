from .models.application import GuardicoreApplication
from ..utils.import_logic import run_import_loop

async def main(name: str):
    return await run_import_loop(
        destination_table='GuardicoreApplications',
        api_endpoint='api/v3.0/workflow/projects',
        method='GET',
        params={},
        model_class=GuardicoreApplication,
        add_sampling_timestamp=True,
    )
