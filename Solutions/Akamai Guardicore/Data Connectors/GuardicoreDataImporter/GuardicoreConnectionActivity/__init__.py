import datetime
import os
import croniter
from datetime import UTC, datetime

from ..utils.import_logic import run_import_loop
from .models.connection import GuardicoreConnection


async def main(name: str):
    connections_last_time = int(name)
    scheduled_run = os.environ.get("Schedule", "*/20 * * * *")

    cron = croniter.croniter(scheduled_run, datetime.now(tz=UTC))
    cron.get_prev(datetime)  # skip prev
    before_prev_iteration_timestamp = cron.get_prev(datetime).timestamp() * 1000

    if connections_last_time == 0:
        connections_last_time = before_prev_iteration_timestamp

    last_connection_time = int(connections_last_time)
    if last_connection_time < before_prev_iteration_timestamp:
        last_connection_time = before_prev_iteration_timestamp

    return await run_import_loop(
        destination_table='GuardicoreConnections',
        api_endpoint='api/v3.0/connections',
        method='GET',
        params={
            'from_time': last_connection_time,
            'to_time': int(datetime.now(tz=UTC).timestamp()) * 1000,
            'sort': 'slot_start_time'
        },
        model_class=GuardicoreConnection,
        add_sampling_timestamp=False,
        field_name_for_last_timestamp='slot_start_time',
        chunk_size=4000,
    )
