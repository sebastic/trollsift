#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014

# Author(s):

# Panu Lahtinen <panu.lahtinen@fmi.fi>
# Hróbjartur Thorsteinsson <thorsteinssonh@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


'''Parser class
'''

import re
import datetime as dt

class Parser(object):
    '''Parser class
    '''

    def __init__(self, fmt):
        self.fmt = fmt

    def parse(self, stri):
        '''Parse keys and corresponding values from *stri* using format
        described in *fmt* string.
        '''
        return parse(self.fmt, stri)

    def compose(self, keyvals):
        '''Return string composed according to *fmt* string and filled
        with values with the corresponding keys in *keyvals* dictionary.
        '''
        return compose(self.fmt, keyvals)

    def validate(self, stri):
        """
        Validates that string *stri* is parsable and therefore complies with
        this string format definition.  Useful for filtering strings, or to 
        check if a string if compatible before passing it to the
        parser function.
        """
        return validate(self.fmt, stri)


def _extract_parsedef(fmt):
    '''Retrieve parse definition from the format string *fmt*.
    '''

    parsedef = []
    convdef = {}

    for part1 in fmt.split('}'):
        for part2 in part1.split('{'):
            if part2 is not '':
                if ':' in part2:
                    part2 = part2.split(':')
                    parsedef.append({part2[0]: part2[1]})
                    convdef[part2[0]] = part2[1]
                else:
                    reg = re.search('(\{'+part2+'\})', fmt)
                    if reg:
                        parsedef.append({part2: None})
                    else:
                        parsedef.append(part2)

    return parsedef, convdef


def _extract_values(parsedef, stri):
    """
    Given a parse definition *parsedef* match and extract key value
    pairs from input string *stri*.
    """
    if len(parsedef) == 0:
        return {}

    match = parsedef.pop(0)
    # we allow ourselves typechecking
    # in case of this hidden subroutine
    if isinstance(match, str):
        # match
        if stri.find(match) == 0:
            stri_next = stri[len(match):]
            return _extract_values( parsedef, stri_next )
        else:
            raise ValueError
    else:
        key = list(match)[0]
        fmt = match[key]
        if (fmt is None) or (fmt.isalpha()):
            next_match = parsedef[0]
            value = stri[0:stri.find(next_match)]
            stri_next = stri[len(value):]
            keyvals =  _extract_values( parsedef, stri_next )
            keyvals[key] = value
            return keyvals
        else:
            # find number of chars
            num = _get_number_from_fmt(fmt)
            value = stri[0:num]
            stri_next = stri[len(value):]
            keyvals =  _extract_values( parsedef, stri_next )
            keyvals[key] = value
            return keyvals

def _get_number_from_fmt(fmt):
    """
    Helper function for _extract_values, 
    figures out string length from format string.
    """
    if '%' in fmt:
        # its datetime
        return len(("{0:"+fmt+"}").format(dt.datetime.now()))
    else:
        # its something else
        fmt = fmt.lstrip('0')
        return int(re.search('[0-9]+', fmt).group(0))


def _convert(convdef, stri):
    '''Convert the string *stri* to the given conversion definition
    *convdef*.
    '''

    if '%' in convdef:
        result = dt.datetime.strptime(stri, convdef)
    elif 'd' in convdef:

        if '>' in convdef:
            stri = stri.lstrip(convdef[0])
        elif '<' in convdef:
            stri = stri.rstrip(convdef[0])
        elif '^' in convdef:
            stri = stri.strip(convdef[0])
        else:
            pass

        result = int(stri)
    else:
        result = stri
    return result


def parse(fmt, stri):
    '''Parse keys and corresponding values from *stri* using format
    described in *fmt* string.
    '''

    parsedef, convdef  = _extract_parsedef(fmt)
    keyvals = _extract_values(parsedef, stri)    

    for key in convdef.keys():        
        keyvals[key] = _convert(convdef[key], keyvals[key])

    return keyvals

def compose(fmt, keyvals):
    '''Return string composed according to *fmt* string and filled
    with values with the corresponding keys in *keyvals* dictionary.
    '''
    return fmt.format(**keyvals)

def validate(fmt, stri):
    """
    Validates that string *stri* is parsable and therefore complies with
    the format string, *fmt*.  Useful for filtering string, or to 
    check if string if compatible before passing the string to the
    parser function.
    """
    try:
        parse(fmt, stri)
        return True
    except ValueError:
        return False


        
