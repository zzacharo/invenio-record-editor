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

"""Invenio module for editing JSON records."""
from .contrib.validators.rules import check_for_author_or_corporate_author_to_exist,\
    check_document_type_if_book_series_exist, check_document_type_if_isbns_exist,\
    check_document_type_if_cnum_exist, check_document_type_if_thesis_info_exist,\
    check_affiliations_if_authors_exist, check_thesis_info_if_doctype_value_thesis_present, \
    check_cnum_if_doctype_value_proceedings_present, check_accelerator_experiments_if_collaborations_exist,\
    check_cnum_if_doctype_value_conference_paper_present, check_doctype_values_if_cnum_present,\
    check_if_isbn_exist_in_other_records, check_if_isbn_is_valid, check_external_urls_if_work,\
    check_accelerator_experiments_for_experiment, check_external_dois_if_exist,\
    check_if_reportnumber_exist_in_other_records, check_if_2_cnum_exist_in_publication_info,\
    check_date_present_in_record, check_if_no_pages_for_publication_info, check_if_journal_title_is_canonical

RECORD_EDITOR_INDEX_TEMPLATE = 'invenio_record_editor/index.html'

RECORD_EDITOR_VALIDATOR_FNS = [
    check_for_author_or_corporate_author_to_exist,
    check_document_type_if_book_series_exist,
    check_document_type_if_isbns_exist,
    check_document_type_if_cnum_exist,
    check_document_type_if_thesis_info_exist,
    check_affiliations_if_authors_exist,
    check_thesis_info_if_doctype_value_thesis_present,
    check_cnum_if_doctype_value_proceedings_present,
    check_cnum_if_doctype_value_conference_paper_present,
    check_doctype_values_if_cnum_present,
    check_accelerator_experiments_if_collaborations_exist,
    check_if_isbn_exist_in_other_records,
    check_if_isbn_is_valid,
    check_external_urls_if_work,
    check_accelerator_experiments_for_experiment,
    check_external_dois_if_exist,
    check_if_reportnumber_exist_in_other_records,
    check_if_2_cnum_exist_in_publication_info,
    check_date_present_in_record,
    check_if_no_pages_for_publication_info,
    check_if_journal_title_is_canonical
]

"""List of validator functions.

NOTE: Each function in validator_fns should have one input parameter
(the record dictionary) and should return a dictionary with the format:
{
    'path.in.dotted.notation': [{
        'message': 'Error/Warning message to be displayed',
        'type': <error|warning>
    }]
}
"""
