r"""
Creates standardized echemdb datapackage compatible CSV.

The file loaded must have the columns t, U/E, and I/j.
Other columns are not included in the output data.

EXAMPLES::

    >>> from io import StringIO
    >>> file = StringIO(r'''t,E,j,x
    ... 0,0,0,0
    ... 1,1,1,1''')
    >>> from .csvloader import CSVloader
    >>> metadata = {'figure description': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}
    >>> ec = ECConverter(CSVloader(file, metadata))
    >>> ec.df
       t  E  j
    0  0  0  0
    1  1  1  1

The original dataframe is still accessible from the loader::

    >>> ec.loader.df
       t  E  j  x
    0  0  0  0  0
    1  1  1  1  1

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


import logging

logger = logging.getLogger("ecconverter")

class ECConverter:
    """
    Creates standardized echemdb datapackage compatible CSV.

    The file loaded must have the columns t, U/E, and I/j.
    Any other columns will be discarded.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO(r'''t,E,j,x
        ... 0,0,0,0
        ... 1,1,1,1''')
        >>> from .csvloader import CSVloader
        >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
        >>> ec = ECConverter(CSVloader(file=file, metadata=metadata, fields=metadata['figure description']['schema']['fields']))
        >>> ec.df
           t  E  j
        0  0  0  0
        1  1  1  1

    A list of names describing the columns::

        >>> ec.column_names
        ['t', 'E', 'j']

        >>> ec.schema['fields']
        [{'name': 't', 'unit': 's'}, {'name': 'E', 'unit': 'V', 'reference': 'RHE'}, {'name': 'j', 'unit': 'uA / cm2'}]

        >>> ec.schema.field_names
        ['t', 'E', 'j']

    """

    def __init__(self, loader, fields=None):
        self.loader = loader
        self._fields = fields

    @property
    def fields(self):
        if not self._fields:
            return self.loader.fields

        return self._fields

    @staticmethod
    def get_converter(device=None):
        r"""
        Calls a specific `converter` based on a given device.
        """
        # import here to avoid cyclical dependencies
        # TODO: Implement the following converters
        # TODO: from .thiolab_labview_converter import ThiolabLabviewConverter
        # TODO: from .genericcsvconverter import GenericCsvConverter
        # TODO: from .eclabconverter import EclabConverter
        # The following dict is a placeholder for further specific converters.
        # They hare here to get an idea what this function should do. These are currently not tested.
        from .eclabconverter import ECLabConverter

        devices = {  #'generic' : GenericCsvLoader, # Generic CSV converter
            "eclab": ECLabConverter,  # Biologic-EClab device
            #'Thiolab Labview' : ThiolabLabviewLoader, # Labview data recorder formerly used in the thiolab
        }

        if device in devices:
            return devices[device]

        raise KeyError(f"Device wth name '{device}' is unknown to the converter'.")

    @property
    def name_conversion(self):
        """
        A dictionary which defines new names for column names of the loaded CSV.
        For example the loaded CSV could contain a column with name `time/s`.
        In the converted CSV that column should be names `t` instead.
        In that case {'time/s':'t'} should be returned.
        The property should be adapted in the respective device converters.


        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> ec = ECConverter(CSVloader(file))
            >>> ec.name_conversion
            {}
        """
        return {}

    @classmethod
    def _validate_core_dimensions(cls, column_names):
        """
        Validates that the column names contain a time, voltage and current axis.

        EXAMPLES::

            >>> ECConverter._validate_core_dimensions(['t','U','I'])
            True

            >>> ECConverter._validate_core_dimensions(['t','U'])
            Traceback (most recent call last):
            ...
            KeyError: "No column with a 'current' axis."

        """
        core_dimensions = {"time": ["t"], "voltage": ["E", "U"], "current": ["I", "j"]}

        for key, item in core_dimensions.items():
            if not set(item).intersection(set(column_names)):
                raise KeyError(f"No column with a '{key}' axis.")
        return True

    @classmethod
    def get_electrochemistry_dimensions(cls, column_names):
        """
        Creates standardized electrochemistry dataframes.

        The file loaded must have the columns t, U/E, and I/j,
        but may contain any other columns related to the EC data.

        EXAMPLES::

            >>> ECConverter.get_electrochemistry_dimensions(['t', 'y', 'U', 'E', 'x', 'j'])
            ['t', 'E', 'U', 'j']

        """
        cls._validate_core_dimensions(column_names)

        valid_dimensions = {"time": ["t"], "voltage": ["E", "U"], "current": ["I", "j"]}

        available_dimensions = []

        for _, items in valid_dimensions.items():
            for item in items:
                if item in column_names:
                    available_dimensions.append(item)

        return available_dimensions

    @property
    def _schema(self):
        r"""
        A frictionless `Schema` object, including a `Fields` object
        describing the columns of the converted electrochemical data.

        In case the field names were not changed in property:name_conversion:
        the resulting schema is identical to that of the loader.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECConverter(CSVloader(file=file, metadata=metadata, fields=metadata['figure description']['schema']['fields']))
            >>> ec._schema
            {'fields': [{'name': 't', 'unit': 's'}, {'name': 'E', 'unit': 'V', 'reference': 'RHE'}, {'name': 'j', 'unit': 'uA / cm2'}, {'name': 'x', 'unit': 'm'}]}


            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'}]}}}
            >>> ec = ECConverter(CSVloader(file=file, metadata=metadata, fields=metadata['figure description']['schema']['fields']))
            >>> ec._schema
            {'fields': [{'name': 't', 'unit': 's'}, {'name': 'E', 'unit': 'V', 'reference': 'RHE'}, {'name': 'j', 'unit': 'uA / cm2'}, {'name': 'x', 'comment': 'Created by echemdb-converters.'}]}

        """
        schema = self.loader.schema

        for name in schema.field_names:
            if name in self.name_conversion:
                schema.get_field(name)["name"] = self.name_conversion[name]

        return schema

    @property
    def schema(self):
        """
        A frictionless `Schema` object, including a `Fields` object
        describing the columns of the converted electrochemical data.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECConverter(CSVloader(file=file, metadata=metadata, fields=metadata['figure description']['schema']['fields']))
            >>> ec.schema
            {'fields': [{'name': 't', 'unit': 's'}, {'name': 'E', 'unit': 'V', 'reference': 'RHE'}, {'name': 'j', 'unit': 'uA / cm2'}]}

        """
        from frictionless import Schema

        schema = Schema(
            fields=[
                self._schema.get_field(name)
                for name in self.get_electrochemistry_dimensions(
                    self._schema.field_names
                )
            ]
        )

        return schema

    @property
    def column_names(self):
        """
        The EC file must have at least three dimensions, including time, voltage and current.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECConverter(CSVloader(file, metadata))
            >>> ec.column_names
            ['t', 'E', 'j']

        """
        return self.schema.field_names

    @property
    def _df(self):
        """
        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}
            >>> ec = ECConverter(CSVloader(file, metadata))
            >>> ec._df
               t  E  j  x
            0  0  0  0  0
            1  1  1  1  1

        """
        df = self.loader.df.copy()
        df.columns = self._schema.field_names
        return df

    @property
    def df(self):
        """
        Creates standardized electrochemistry dataframes.

        The file loaded must have the columns t, U/E, and I/j.
        Any other columns are discarded.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}
            >>> ec = ECConverter(CSVloader(file, metadata))
            >>> ec.df
               t  E  j
            0  0  0  0
            1  1  1  1

        """
        return self._df[self.column_names]
