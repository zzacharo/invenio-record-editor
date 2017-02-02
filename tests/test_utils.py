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


"""Utils tests."""

from __future__ import absolute_import, print_function

from helpers import multiple_error_check, other_simple_check, simple_check
from invenio_record_editor.utils import RecordValidator


def test_record_validator_with_simple_check():
    record = {
        "hello": "world"
    }
    expected = {
        "hello": [{
            'message': 'Hello should not be equal to world',
            'type': 'warning'
        }]
    }
    record_validator = RecordValidator(
        record=record,
        validator_fns=[simple_check]
    )
    record_validator.validate()
    assert expected == dict(record_validator.errors)


def test_record_validator_with_multiple_checks_in_same_field():
    record = {
        "hello": "world"
    }
    expected = {
        "hello": [
            {
                'message': 'Hello should not be equal to world',
                'type': 'warning'
            },
            {
                'message': 'Hello and world are not compatible',
                'type': 'error'
            }
        ]
    }
    record_validator = RecordValidator(
        record=record,
        validator_fns=[simple_check, other_simple_check]
    )
    record_validator.validate()
    assert expected == dict(record_validator.errors)


def test_record_validator_with_checks_that_return_multiple_errors_in_key():
    record = {
        "hello": "world"
    }
    expected = {
        "hello": [
            {
                'message': 'Hello should not be equal to world',
                'type': 'warning'
            },
            {
                'message': 'Hello and world are not compatible',
                'type': 'error'
            },
            {
                'message': 'This field also contains a warning',
                'type': 'warning'
            }

        ]
    }
    record_validator = RecordValidator(
        record=record,
        validator_fns=[simple_check, multiple_error_check]
    )
    record_validator.validate()
    assert expected == dict(record_validator.errors)


def test_record_validator_with_no_errors():
    record = {
        "hello": "universe"
    }
    expected = {}
    record_validator = RecordValidator(
        record=record,
        validator_fns=[simple_check, other_simple_check]
    )
    record_validator.validate()
    assert expected == dict(record_validator.errors)
