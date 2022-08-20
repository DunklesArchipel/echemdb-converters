r"""
Loads MPT files recorded with the EC-Lab software from BioLogic for BioLogic potentiostats.

EXAMPLES:

The file can be loaded with the ECLabPackager::

    >>> from io import StringIO
    >>> file = StringIO('''EC-Lab ASCII FILE
    ... Nb header lines : 6
    ...
    ... Device metadata : some metadata
    ...
    ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
    ... 2\t0\t0.1\t0\t0
    ... 2\t1\t1.4\t5\t1
    ... ''')
    >>> eclab_csv = ECLabPackager(file)
    >>> eclab_csv.df
        mode  time/s Ewe/V  <I>/mA  control/V
    0     2       0   0.1       0          0
    1     2       1   1.4       5          1

The file can also be loaded from the base packager::

    >>> from io import StringIO
    >>> file = StringIO('''EC-Lab ASCII FILE
    ... Nb header lines : 6
    ...
    ... Device metadata : some metadata
    ...
    ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
    ... 2\t0\t0.1\t0\t0
    ... 2\t1\t1.4\t5\t1
    ... ''')
    >>> from ..csvpackager import CSVpackager
    >>> csv = CSVpackager.get_packager('eclab')(file)
    >>> csv.df
        mode  time/s Ewe/V  <I>/mA  control/V
    0     2       0   0.1       0          0
    1     2       1   1.4       5          1

    >>> csv.header
    ['EC-Lab ASCII FILE\n', 'Nb header lines : 6\n', '\n', 'Device metadata : some metadata\n', '\n']

    >>> csv.column_names
    ['mode', 'time/s', 'Ewe/V', '<I>/mA', 'control/V']

"""
# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2022 Albert Engstfeld
#        Copyright (C) 2022 Johannes Hermann
#        Copyright (C) 2022 Julian Rüth
#
#  echemdb-converters is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb-converters is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb-converters. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************


from ..csvpackager import CSVpackager

biologic_fields = [
    {
        "name": "mode",
    },
    {
        "name": "ox/red",
    },
    {
        "name": "error",
    },
    {
        "name": "control changes",
    },
    {
        "name": "counter inc.",
    },
    {"name": "time/s", "unit": "s", "dimension": "t", "description": "relative time"},
    {
        "name": "control/V",
        "unit": "V",
        "dimension": "E",
        "description": "control voltage",
    },
    {
        "name": "Ewe/V",
        "unit": "V",
        "dimension": "E",
        "description": "working electrode potential",
    },
    {
        "name": "<I>/mA",
        "unit": "mA",
        "dimension": "I",
        "description": "working electrode current",
    },
    {"name": "cycle number", "description": "cycle number"},
    {
        "name": "(Q-Qo)/C",
        "unit": "C",
    },
    {"name": "I Range", "description": "current range"},
    {"name": "P/W", "unit": "W", "dimension": "P", "description": "power"},
    {
        "name": "Unnamed: 13",  # It seems that there is an unnamed column in the csv where the number reflects the number of columns.(see: #8)
    },
]


class ECLabPackager(CSVpackager):
    r"""
    Loads BioLogic EC-Lab MPT files.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO('''EC-Lab ASCII FILE
        ... Nb header lines : 6
        ...
        ... Device metadata : some metadata
        ...
        ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
        ... 2\t0\t0.1\t0\t0
        ... 2\t1\t1.4\t5\t1
        ... ''')
        >>> from ..csvpackager import CSVpackager
        >>> csv = CSVpackager.get_packager('eclab')(file)
        >>> csv.df
           mode  time/s Ewe/V  <I>/mA  control/V
        0     2       0   0.1       0          0
        1     2       1   1.4       5          1

        >>> csv.header
        ['EC-Lab ASCII FILE\n', 'Nb header lines : 6\n', '\n', 'Device metadata : some metadata\n', '\n']

        >>> csv.column_names
        ['mode', 'time/s', 'Ewe/V', '<I>/mA', 'control/V']

    """

    @property
    def header_lines(self):
        r"""
        The number of header lines of an EC-Lab MPT file without column names.
        The number is provided in the header of the MPT file, which contains, however,
        also the line with the data column names.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0.1\t0\t0
            ... 2\t1\t1.4\t5\t1
            ... ''')
            >>> from ..csvpackager import CSVpackager
            >>> csv = CSVpackager.get_packager('eclab')(file)
            >>> csv.header_lines
            5

        """
        matches = []

        for line in self.file.readlines():
            import re

            match = re.findall(
                r"(?P<headerlines>Nb header lines) *\: *(?P<value>-?\d+\.?\d*)",
                str(line),
                re.IGNORECASE,
            )

            if match:
                matches.append(match)

        return int(matches[0][0][1]) - 1

    @property
    def df(self):
        r"""
        A pandas dataframe with the data of the EC-Lab MPT file.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0.1\t0\t0
            ... 2\t1\t1.4\t5\t1
            ... ''')
            >>> from ..csvpackager import CSVpackager
            >>> csv = CSVpackager.get_packager('eclab')(file)
            >>> csv.df
               mode  time/s Ewe/V  <I>/mA  control/V
            0     2       0   0.1       0          0
            1     2       1   1.4       5          1

        """
        import pandas as pd

        return pd.read_csv(
            self.file,
            sep=self.delimiter,
            header=self.header_lines,
            decimal=self.decimal,
            encoding="latin1",
            skip_blank_lines=False,
        )

    def create_fields(self):
        r"""
        Creates a list of fields from possible BiLogic field names provided :value:biologic_fields.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0.1\t0\t0
            ... 2\t1\t1.4\t5\t1
            ... ''')
            >>> from ..csvpackager import CSVpackager
            >>> ec = CSVpackager.get_packager('eclab')(file)
            >>> ec.create_fields() # doctest: +NORMALIZE_WHITESPACE
            [{'name': 'mode'}, {'name': 'time/s', 'unit': 's', 'dimension': 't', 'description': 'relative time'},
            {'name': 'control/V', 'unit': 'V', 'dimension': 'E', 'description': 'control voltage'},
            {'name': 'Ewe/V', 'unit': 'V', 'dimension': 'E', 'description': 'working electrode potential'},
            {'name': '<I>/mA', 'unit': 'mA', 'dimension': 'I', 'description': 'working electrode current'}]

        """
        # TODO:: When the file contains an unnamed column an this is not 13, this approach will fail. (see: #8)
        return [
            field
            for field in biologic_fields
            for name in self.column_names
            if name == field["name"]
        ]

    @property
    def decimal(self):
        r"""
        Returns the decimal separator in the MPT,
        which depends on the language settings of the operating system running the software.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> from ..csvpackager import CSVpackager
            >>> ec = CSVpackager.get_packager('eclab')(file)
            >>> ec.decimal
            ','

        """
        # The values in the MPT are always tab separated.
        # The data in the file only consist of numbers.
        # Hence we simply determine if the line contains a comma or not.
        if "," in self.data.readlines()[0]:
            return ","

        return "."
