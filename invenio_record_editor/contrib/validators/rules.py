#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

'''Validator classes for Invenio Record Editor.'''

from __future__ import absolute_import, division, print_function
from .helpers import check_if_field_exists_in_dict_list_x_times, check_field_values_not_in_required_values_for_record,\
    FIELD_VALUE_REQUIRE_FIELD_TEMPLATE, FIELD_REQUIRE_FIELD_TEMPLATE, FIELD_REQUIRE_FIELD_VALUES_TEMPLATE,\
    check_if_listfield_property_are_valid, query_db_for_duplicates_for_field_listitem_with_index,\
    ISBN_IS_VALID_TEMPLATE, FIELD_VALIDATION_TEMPLATE, DOI_VALIDATION_URL, SCHEMA_FIELDS_THAT_CAN_CONTAIN_DATE,\
    GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE, get_query_results_if_exceed_limit
from .errors import ValidationError
from idutils import is_isbn
from requests.exceptions import ConnectionError
import requests
import six

'''
Error Validator Functions
'''


def check_for_author_or_corporate_author_to_exist(record):
    if all(k not in record for k in ['authors', 'corporate_author']):
        raise ValidationError(key='globalErrors',
                              message='Neither an author nor a corporate author found.')

    return {}


def check_document_type_if_book_series_exist(record):
    if 'book_series' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='book_series',
                                      required='document_type',
                                      values=required_values))
    return {}


def check_document_type_if_isbns_exist(record):
    if 'isbns' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='isbns',
                                      required='document_type',
                                      values=required_values))
    return {}


def check_document_type_if_cnum_exist(record):
    if check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
        required_values = ['proceedings', 'conference paper']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='cnum',
                                      required='document_type',
                                      values=required_values))

    return {}


def check_document_type_if_thesis_info_exist(record):
    if 'thesis_info' in record:
        required_values = ['thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='thesis_info',
                                      required='document_type',
                                      values=required_values))
    return {}


def check_if_isbn_is_valid(record):
    def _check_isbn_is_valid(field, value, property, index, errortype):
        if not is_isbn(value):
            raise ValidationError(key='/{field}/{index}/{property}'.format(field='isbns',
                                                                           property=property,
                                                                           index=index),
                                  message=ISBN_IS_VALID_TEMPLATE.format(
                                      isbn=value
                                  ))
        return {}

    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='isbns',
                                              property='value',
                                              checker=_check_isbn_is_valid)
    except ValidationError:
        raise
    return {}


# TODO: Consider if this should error or warning
def check_if_isbn_exist_in_other_records(record):
    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='isbns',
                                              property='value',
                                              checker=query_db_for_duplicates_for_field_listitem_with_index)
    except ValidationError:
        raise
    return {}


def check_date_present_in_record(record):
    for field, properties in six.iteritems(SCHEMA_FIELDS_THAT_CAN_CONTAIN_DATE):
        if field in record:
            if properties:
                for prop in properties:
                    if check_if_field_exists_in_dict_list_x_times(prop, record[field], 1):
                        # return after 1st occurrence
                        return {}
            else:
                return {}
    raise ValidationError(key='globalErrors',
                          message='No date present.')


def check_if_journal_title_is_canonical(record):
    def _check_for_journal_title(field, property, value, index, errortype):
        querystring = GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE.format(field=field,
                                                                                 property=property,
                                                                                 value=value)
        results = get_query_results_if_exceed_limit(querystring, 0)
        if not results:
            raise ValidationError(key='/{field}/{index}'.format(field=field, index=index),
                                  message="Journal title '{title}' doesn't exist.'".format(title=value),
                                  type=errortype)
    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='publication_info',
                                              property='journal_title',
                                              checker=_check_for_journal_title)
    except ValidationError:
        raise
    return {}


'''
Warnings Validator Functions
'''


def check_affiliations_if_authors_exist(record):
    def _check_affiliations_for_author(author, index):
        if 'affiliations' not in author or len(author['affiliations']) == 0:
            raise ValidationError(key='/authors/{index}'.format(index=index),
                                  message=FIELD_REQUIRE_FIELD_TEMPLATE.format(
                                      field='authors',
                                      required='affiliations'),
                                  type='Warning')

    affiliations_warnings = {}
    if 'authors' in record:
        for i, author in enumerate(record['authors']):
            try:
                _check_affiliations_for_author(author, i)
            except ValidationError as e:
                affiliations_warnings.update(e.error)

        if affiliations_warnings:
            raise ValidationError(error=affiliations_warnings)
    return affiliations_warnings


def check_thesis_info_if_doctype_value_thesis_present(record):
    doctype_values = record.get('document_type', [])
    if 'thesis' in doctype_values:
        if not 'thesis_info' in record:
            raise ValidationError(key='globalErrors',
                                  message=FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
                                      field='document_type',
                                      value='thesis',
                                      required='thesis_info'),
                                  type='Warning')
    return {}


def check_cnum_if_doctype_value_proceedings_present(record):
    doctype_values = record.get('document_type', [])
    if 'proceedings' in doctype_values:
        if not check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
                                      field='document_type',
                                      value='proceedings',
                                      required='cnum'),
                                  type='Warning')
    return {}


def check_cnum_if_doctype_value_conference_paper_present(record):
    doctype_values = record.get('document_type', [])
    if 'conference paper' in doctype_values:
        if not check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
                                      field='document_type',
                                      value='conference paper',
                                      required='cnum'),
                                  type='Warning')
    return {}


def check_if_2_cnum_exist_in_publication_info(record):
    if check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', []), limit=2):
        raise ValidationError(key='globalErrors',
                              message="2 cnums found in 'publication info' field.",
                              type='Warning')


def check_doctype_values_if_cnum_present(record):
    if check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
        required_values = ['proceedings', 'conference_paper']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='cnum',
                                      required='document_type',
                                      values=required_values),
                                  type='Warning')
    return {}


def check_accelerator_experiments_if_collaborations_exist(record):
    if 'collaborations' in record:
        if not 'accelerator_experiments' in record:
            raise ValidationError(key='globalErrors',
                                  message=FIELD_REQUIRE_FIELD_TEMPLATE.format(
                                      field='collaborations',
                                      required='accelerator_experiments'),
                                  type='Warning')
    return {}


def check_if_reportnumber_exist_in_other_records(record):
    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='report_numbers',
                                              property='value',
                                              checker=query_db_for_duplicates_for_field_listitem_with_index,
                                              errortype='Warning')
    except ValidationError:
        raise
    return {}


def check_external_urls_if_work(record):
    def _check_if_url_works(field, property, value, index, errortype):
        try:
            resp = requests.get(value)
            if not resp.ok:
                raise ConnectionError
        except ConnectionError:
            raise ValidationError(key='/{field}/{index}/{property}'.format(field=field, property=property, index=index),
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='urls',
                                      value=value
                                  ),
                                  type=errortype)
        return {}

    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='urls',
                                              property='value',
                                              checker=_check_if_url_works,
                                              errortype='Warning'
                                              )
    except ValidationError:
        raise
    return {}


def check_external_dois_if_exist(record):
    def _check_if_doi_works(field, property, value, index, errortype):
        doi_url = DOI_VALIDATION_URL.format(doi=value)
        try:
            resp = requests.get(doi_url)
            if not resp.ok:
                raise ConnectionError
        except ConnectionError:
            raise ValidationError(key='/{field}/{index}/{property}'.format(field=field, property=property, index=index),
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='dois',
                                      value=value
                                  ),
                                  type=errortype)
        return {}

    try:
        check_if_listfield_property_are_valid(record=record,
                                              field='dois',
                                              property='value',
                                              checker=_check_if_doi_works,
                                              errortype='Warning'
                                              )
    except ValidationError:
        raise
    return {}


def check_accelerator_experiments_for_experiment(record):
    if 'accelerator_experiments' in record:
        for experiment in record['accelerator_experiments']:
            if 'experiment' in experiment:
                return {}
        raise ValidationError(key='globalErrors',
                              message="'accelerator_experiments' field should have at least one experiment")
    return {}


def check_thesis_info_and_supervisor_to_exist_in_thesis(record):
    doctype_values = record.get('document_type', [])
    if 'thesis' in doctype_values:
        if 'thesis_info' not in record and 'supervisor' not in record.get('inspire_roles', []):
            raise ValidationError(key='globalErrors',
                                  message="Thesis should have both 'thesis_info' and 'supervisor' field.")
    return {}


def check_if_no_pages_for_publication_info(record):
    def _check_for_pages(publication, index):
        if all(k not in publication for k in ['page_start', 'page_end']):
            raise ValidationError(key='/publication_info/{index}'.format(index=index),
                                  message="Missing 'page_start' or 'page_end' field.",
                                  type='Warning')

    invalid_dict = {}
    for i, publication in enumerate(record.get('publication_info', [])):
        try:
            _check_for_pages(publication, i)
        except ValidationError as e:
            invalid_dict.update(e.error)
    if invalid_dict:
        raise ValidationError(error=invalid_dict)
    return {}
