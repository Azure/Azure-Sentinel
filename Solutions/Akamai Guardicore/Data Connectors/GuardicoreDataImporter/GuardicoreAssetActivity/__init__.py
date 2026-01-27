from .models.asset import GuardicoreAsset
from ..utils.import_logic import run_import_loop


async def main(name: str):
    return await run_import_loop(
        destination_table='GuardicoreAssets',
        api_endpoint='api/v3.0/assets',
        method='GET',
        params={},
        model_class=GuardicoreAsset,
        add_sampling_timestamp=True,
    )
