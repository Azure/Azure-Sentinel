from .models.label import GuardicoreLabel
from ..utils.import_logic import run_import_loop


async def main(name: str):
    return await run_import_loop(
        destination_table='GuardicoreLabels',
        api_endpoint='api/v4.0/labels',
        method='GET',
        params={},
        model_class=GuardicoreLabel,
        add_sampling_timestamp=True,
    )
