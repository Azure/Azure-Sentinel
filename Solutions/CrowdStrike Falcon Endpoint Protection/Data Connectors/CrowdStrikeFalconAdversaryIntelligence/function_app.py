import azure.functions as func
from CrowdStrikeFalconThreatIntelConnector.main import run

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */10 * * * *",
    arg_name="mytimer",
    run_on_startup=False,
)
def CrowdStrikeFalconThreatIntelConnector(mytimer: func.TimerRequest) -> None:
    run(mytimer)
