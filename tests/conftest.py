# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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


"""Pytest configuration."""

from __future__ import absolute_import, print_function
from flask import Flask
import pytest
import os
import tempfile
import shutil
from invenio_pidstore import InvenioPIDStore
from invenio_record_editor import InvenioRecordEditor
from invenio_db import InvenioDB
from invenio_records import InvenioRecords
from invenio_indexer import InvenioIndexer
from invenio_search import InvenioSearch


@pytest.fixture(scope="session")
def app():
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask(__name__, instance_path=instance_path)
    app.config.update(
        TESTING=True
    )
    InvenioRecordEditor(app)
    InvenioPIDStore(app)
    InvenioDB(app)
    InvenioRecords(app)
    InvenioIndexer(app)
    InvenioSearch(app)
    with app.app_context():
        yield app
        shutil.rmtree(instance_path)

        
@pytest.fixture(scope="session")
def app_client(app):
    """Flask test client for app."""
    with app.test_client() as client:
        yield client
