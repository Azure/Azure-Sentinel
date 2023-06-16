# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# ==========================================================================
# This file contains duplicate code that is shared with azure-eventgrid.
# Both the files should always be identical.
# ==========================================================================


import json
from azure.core.exceptions import raise_with_traceback


def _get_json_content(obj):
    """Event mixin to have methods that are common to different Event types
    like CloudEvent, EventGridEvent etc.
    """
    msg = "Failed to load JSON content from the object."
    try:
        # storage queue
        return json.loads(obj.content)
    except ValueError as err:
        raise_with_traceback(ValueError, msg, err)
    except AttributeError:
        # eventhubs
        try:
            return json.loads(next(obj.body))[0]
        except KeyError:
            # servicebus
            return json.loads(next(obj.body))
        except ValueError as err:
            raise_with_traceback(ValueError, msg, err)
        except:  # pylint: disable=bare-except
            try:
                return json.loads(obj)
            except ValueError as err:
                raise_with_traceback(ValueError, msg, err)
