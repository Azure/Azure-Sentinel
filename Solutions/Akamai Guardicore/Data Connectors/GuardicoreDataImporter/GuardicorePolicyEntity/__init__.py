from ..utils.import_logic import run_import_loop
from .models.rule import GuardicorePolicyRule


async def main(name: str):
    return await run_import_loop(
        destination_table='GuardicorePolicyRules',
        api_endpoint='api/v4.0/visibility/policy/rules',
        method='GET',
        params={},
        model_class=GuardicorePolicyRule,
        add_sampling_timestamp=True,
    )
