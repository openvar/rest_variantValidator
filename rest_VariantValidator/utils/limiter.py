from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

limiter = Limiter(key_func=get_remote_address)

_running_vals = {}
def concurrency_limit():
    """Wrapper for decorating in order to stop parallel requests

    Currently relies on the IP we will need to change this if we
    want to do limits per login. "_running_vals" should only bloat if
    we get hard crashes.
    """
    def decorator(handler):
        def wrapper(*args, **kwargs):
            """
            Store the IP address source of running validations, if a user is
            already running a validation block use until finished, remove
            stored IP before returning.
            """
            ip_address = request.remote_addr
            if ip_address in _running_vals:
                err = 'Concurrency limit exceeded. Please try again once " + \
                        "your existing API requests have completed.'
                return {"message":err }, 429

            _running_vals[ip_address] = 1
            result = handler(*args, **kwargs)
            del _running_vals[ip_address]
            return result
        return wrapper
    return decorator

# <LICENSE>
# Copyright (C) 2016-2025 VariantValidator Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# </LICENSE>
