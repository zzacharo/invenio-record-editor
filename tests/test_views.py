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


"""Module tests."""

from __future__ import absolute_import, print_function
import pytest
import json
from invenio_pidstore.models import PersistentIdentifier as PI
from invenio_records.models import RecordMetadata as RM
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_records.api import Record
from invenio_db import db as db_
from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture(scope='session')
def db(app):
    """Database fixture."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.fixture(scope='session')
def generate_data(app, db):
    
    schema = {
        "$schema": "http://json-schema.org/schema#",
        "description": "Sample schema for testing",
        "properties": {
            "titles": {
                "items": {
                    "properties": {
                        "source": {
                            "type": "string"
                        },
                        "subtitle": {
                            "type": "string"
                        },
                        "title": {
                            "type": "string"
                        }
                    },
                    "type": "object"
                },
                "type": "array",
            }
        }
    }
    record_data = {
        "$schema": schema,
        "titles": [
            {
                "title": "Cosmic Antigravity"
            }
        ]
    }
    json_data = {
        "pid_type": "testSaveView",
        "recid": 1,
        "json_data": record_data
    }

    with app.app_context():
        try:
            assert RM.query.count() == 0
            record = Record.create(json_data)
            record_uuid = record.id
            record.commit()

            assert PI.query.count() == 0
            pid = PI.create(json_data["pid_type"], json_data[
                "recid"], object_type="rec", object_uuid=record_uuid)
            db.session.commit()
            assert pid.pid_type == "testSaveView"
            assert pid.id == 1
    
            yield json_data

            record.delete(force=True)
            pid.delete()
            assert PI.query.count() == 0
            assert RM.query.count() == 0
        except AssertionError:
            raise Exception("Record or PersistentIdentifier haven't deleted correctly")


def test_that_generated_data_initialized_properly(generate_data):
    try:
        pid = PI.get(generate_data["pid_type"], generate_data["recid"])
        rec = Record.get_record(pid.object_uuid)
        assert rec.id == pid.object_uuid
    except AssertionError as e:
        raise Exception(e)


def test_save_view_does_not_accept_get_request(app, app_client):
    res = app_client.get("/editor/save")
    assert res.status_code == 405


def test_save_view_request_valid_schema_data(app, app_client, generate_data):
    res = app_client.post("/editor/save", data=json.dumps(generate_data))
    res_data = json.loads(res.data)
    assert res.status_code == 200
    assert res_data["status"] == 200
    assert res_data["message"] == "Record saved successfully"

def test_save_view_request_invalid_schema_data(app, app_client, generate_data):
    generate_data["json_data"]["titles"][0]["title"] = 0
    res = app_client.post("/editor/save", data=json.dumps(generate_data))
    res_data = json.loads(res.data)
    assert res.status_code == 200
    assert res_data["status"] == 500
    expected_error_map = json.loads(json.dumps({
        "errorMap": {
            "titles.0.title": [
              {
                "message": "0 is not of type string"
              }
            ]
        },
        "status": 500
    }))
    assert res_data["errorMap"] == expected_error_map["errorMap"]


def test_save_view_request_not_existing_data(app, app_client, generate_data):
    generate_data["pid_type"] = "error"
    res = app_client.post("/editor/save", data=json.dumps(generate_data))
    res_data = json.loads(res.data)
    assert res.status_code == 200
    assert res_data["status"] == 404
    assert res_data["message"] == "Record doesn't exist"
