import json


def format_input(data_string):
    """
    Takes an input string. Tries to convert from JSON to list, otherwise converts a string into a list.
    Then goes on to check for pipe delimited data and splits if necessary
    The output is a JSON array
    """
    data_string = str(data_string)
    try:
        data_list = json.loads(data_string)
    except json.decoder.JSONDecodeError:
        data_intermediate = data_string.replace("|gom", "&gom")
        data_intermediate = data_intermediate.replace("|lom", "&lom")
        pre_data_list = data_intermediate.split("|")
        if not isinstance(pre_data_list, list):
            pre_data_list = [pre_data_list]
        data_list = []
        for entry in pre_data_list:
            entry = entry.replace("&", "|")
            data_list.append(entry)

    return json.dumps(data_list)

# <LICENSE>
# Copyright (C) 2016-2023 VariantValidator Contributors
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
