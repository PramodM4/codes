import json
from flask import request
from connect.fhir.nodes.search_query import SearchQueries
from connect.fhir.nodes.appointment import Appointment, ClockIn, Task

from connect.fhir.utils import (
    execute_graphql,
    create_auth_token,
    json_graphql,
    get_valid_sort_params,
    database_id_from_hash
)
from connect.fhir.nodes.query_constants import CLOCK_IN_MUTATION_QUERY, CLOCK_OUT_MUTATION_QUERY, TASK_MUTATION_QUERY
from connect.fhir.custom_exception import UnprocessableEntity, ResourceNotFound
from .constants import SHIFT_FIELDS_FHIR_CC_MAPPING
from connect.constants import APPOINTMENT_SORT_ALLOWED_FIELDS_LIST


class FhirAppointmentTranslation(object):
    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.get("agency_id", None)
        self.franchise_id = kwargs.get("franchise_id", None)
        self.appointment_id = kwargs.get("appointment_id", None)
        self.data = kwargs.get("data", None)

    def get_appointment(self, appointment_id=None):
        if appointment_id:
            self.appointment_id = appointment_id

        return Appointment(
            token=create_auth_token(agency_id=self.agency_id,
                                    franchise_id=self.franchise_id),
            params={'id': self.appointment_id, },
        ).json


class FhirTaskTranslation(object):
    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.get("agency_id", None)
        self.franchise_id = kwargs.get("franchise_id", None)
        self.task_id = kwargs.get("task_id", None)
        self.data = kwargs.get("data", None)

    def get_task(self, task_id=None):
        if task_id:
            self.task_id = task_id

        return Task(
            token=create_auth_token(agency_id=self.agency_id,
                                    franchise_id=self.franchise_id),
            params={'id': self.task_id, },
        ).json

    def update_task(self):

        graphql_input_dict = dict()
        graphql_input_dict["taskId"] = self.task_id

        for key, value in self.data.iteritems():
            graphql_input_dict[key] = value

        graphql_input_string = json_graphql(graphql_input_dict)[1:-1]
        query = TASK_MUTATION_QUERY.format(graphql_input=graphql_input_string)

        result = execute_graphql(query, token=create_auth_token(
            agency_id=self.agency_id,
            franchise_id=self.franchise_id))

        response = result['createUpdateTask']

        return response


class FhirClockInOutTranslation(object):
    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.get("agency_id", None)
        self.franchise_id = kwargs.get("franchise_id", None)
        self.shift_id = kwargs.get("shift_id", None)
        self.carelog_id = kwargs.get("carelog_id", None)
        self.data = kwargs.get("data", None)

    def create_clock_in(self):

        graphql_input_dict = dict()
        graphql_input_dict["shiftId"] = self.shift_id

        for key, value in self.data.iteritems():
            if key == 'position':
                for k, v in value.iteritems():
                    if k in ('latitude', 'longitude'):
                        graphql_input_dict['{}'.format(k)] = v
            elif key == 'period':
                for k, v in value.iteritems():
                    if k == 'start':
                        graphql_input_dict[SHIFT_FIELDS_FHIR_CC_MAPPING['{}'.format(k)]] = v
            elif key in SHIFT_FIELDS_FHIR_CC_MAPPING:
                graphql_input_dict[SHIFT_FIELDS_FHIR_CC_MAPPING[key]] = value
            elif value:
                graphql_input_dict[key] = value

        graphql_input_string = json_graphql(graphql_input_dict)[1:-1]
        query = CLOCK_IN_MUTATION_QUERY.format(graphql_input=graphql_input_string)

        result = execute_graphql(query, token=create_auth_token(
            agency_id=self.agency_id,
            franchise_id=self.franchise_id))

        response = result['caregiverClockIn']
        output = ClockIn(None).json(response)

        return output

    def create_clock_out(self):

        graphql_input_dict = dict()
        graphql_input_dict["careLogId"] = self.carelog_id

        for key, value in self.data.iteritems():
            if key == 'period':
                for k, v in value.iteritems():
                    if k == 'end':
                        graphql_input_dict[SHIFT_FIELDS_FHIR_CC_MAPPING['{}'.format(k)]] = v
            elif key in SHIFT_FIELDS_FHIR_CC_MAPPING:
                graphql_input_dict[SHIFT_FIELDS_FHIR_CC_MAPPING[key]] = value
            elif value:
                graphql_input_dict[key] = value

        graphql_input_string = json_graphql(graphql_input_dict)[1:-1]
        query = CLOCK_OUT_MUTATION_QUERY.format(graphql_input=graphql_input_string)

        result = execute_graphql(query, token=create_auth_token(
            agency_id=self.agency_id,
            franchise_id=self.franchise_id))

        response = result['caregiverClockOut']

        return response


def search_appointment():
    auth_token = create_auth_token(
        franchise_id=request.args.get('franchiseId'),
        agency_id=request.args.get('agencyId'),
    )
    sort_params = request.args.get('_sort', ",").split(",")
    sort_params = get_valid_sort_params(sort_params, APPOINTMENT_SORT_ALLOWED_FIELDS_LIST)
    query = SearchQueries().get_caregiver_query(sort_params)
    result = execute_graphql(query, token=auth_token)
    appointments = result['shiftSearch']
    entries, totalRecords = Appointment(None).search_json(appointments)

    return {
        "resourceType": "Bundle",
        "id": "searchParams",
        "type": "searchset",
        "totalRecords": totalRecords,
        "entry": entries
    }