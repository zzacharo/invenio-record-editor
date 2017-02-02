# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utils for Invenio Record Editor."""

from collections import defaultdict

import six


class RecordValidator(object):
    """Class for validating a record and generating an error list."""

    def __init__(self, **kwargs):
        """Initialize record validator.

        :param record:  Dictionary representing a record that needs validation
        :type record: dict

        :param validator_fns: Functions that will return validation errors
        :type validator_fns: list

        NOTE: Each function in validator_fns should have one input parameter
        (the record dictionary) and should return a dictionary with the format:
        {
            'path.in.dotted.notation': [{
                'message': 'Error/Warning message to be displayed',
                'type': <error|warning>
            }]
        }

        :raises TypeError: If there are unknown arguments passed to constructor
        """
        self.record = kwargs.pop('record', {})
        self.validator_fns = kwargs.pop('validator_fns', [])
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        self.errors = defaultdict(list)

    def validate(self):
        """Run self.validator_fns and accumulate errors in self.errors."""
        for fn in self.validator_fns:
            errors = fn(self.record)
            for key, error in six.iteritems(errors):
                self.errors[key].extend(error)
