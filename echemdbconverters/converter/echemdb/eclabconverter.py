r"""
Converts ECLab MPT files into an echemdb datapackage compatible CSV object.
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

from .ecconverter import ECConverter


class ECLabConverter(ECConverter):
    r"""
    Some description.

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
        >>> from ...packager.csvpackager import CSVpackager
        >>> ec = ECLabConverter(CSVpackager.get_packager('eclab')(file))
        >>> ec.df
           t  E  I
        0  0  0  0
        1  1  5  1

    """

    @property
    def name_conversion(self):

        return {
            "time/s": "t",
            "Ewe/V": "E",
            "<I>/mA": "I",
        }
