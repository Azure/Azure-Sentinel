import datetime
from ..utils.import_logic import run_import_loop
from .models.incident import GuardicoreIncident


async def main(name: str):
    connections_last_time = int(name)
    if connections_last_time == 0:
        connections_last_time = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=5)
        connections_last_time = connections_last_time.timestamp() * 1000

    last_connection_time = int(connections_last_time)

    return await run_import_loop(
        destination_table='GuardicoreIncidents',
        api_endpoint='api/v3.0/generic-incidents',
        method='GET',
        params={
            'from_time': last_connection_time,
            'to_time': int(datetime.datetime.now(tz=datetime.UTC).timestamp()) * 1000,
        },
        model_class=GuardicoreIncident,
        add_sampling_timestamp=False,
        field_name_for_last_timestamp='time'
    )
