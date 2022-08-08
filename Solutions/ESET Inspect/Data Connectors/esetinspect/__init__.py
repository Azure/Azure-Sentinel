from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from esetinspect.eifunctions import exit_error
from esetinspect.inspect import Inspect as Inspect

# Disable default SSL warning
disable_warnings(InsecureRequestWarning)  # type: ignore
