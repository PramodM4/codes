from flask import request, jsonify, make_response, abort
from werkzeug.exceptions import BadRequest

from connect.fhir.views import BaseFHIRView
from connect.fhir.utils import database_id_to_hash
from connect.fhir.custom_exception import CustomBadRequest, UnprocessableEntity
from .translation import FhirClockInOutTranslation, FhirAppointmentTranslation, search_appointment, FhirTaskTranslation


class FhirAppointment(BaseFHIRView):

    def get(self, appointment_id=None):
        if request.path.strip('/').endswith('_search'):
            abort(405)
        elif appointment_id:
            return self.get_by_id(appointment_id)
        else:
            return self.search()

    def search(self):
        return jsonify(
            search_appointment()
        )

    def get_by_id(self, appointment_id):
        if appointment_id.isdigit():
            database_id = int(appointment_id)
            appointment_id = database_id_to_hash('Shift', database_id)

        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "agency_id": agency_id,
            "franchise_id": franchise_id,
            "appointment_id": appointment_id,
        }

        return jsonify(
            FhirAppointmentTranslation(**kwargs).get_appointment()
        )


class FhirClockIn(BaseFHIRView):

    def get(self, appointment_id=None):
        if request.path.strip('/').endswith('_search'):
            abort(405)
        elif appointment_id:
            return self.get_by_id(appointment_id)
        else:
            return self.search()

    def search(self):
        return jsonify(
            search_appointment()
        )

    def get_by_id(self, appointment_id):
        if appointment_id.isdigit():
            database_id = int(appointment_id)
            appointment_id = database_id_to_hash('Shift', database_id)

        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "agency_id": agency_id,
            "franchise_id": franchise_id,
            "appointment_id": appointment_id,
        }

        return jsonify(
            FhirAppointmentTranslation(**kwargs).get_appointment()
        )

    def post(self, shift_id):

        if shift_id.isdigit():
             shift_id = database_id_to_hash('Shift', int(shift_id))
        else:
             raise UnprocessableEntity("Shift Id needs to be integer.")

        try:
            data = request.get_json(force=True)
        except BadRequest:
            raise CustomBadRequest()

        if data.get('resourceType') != 'Encounter':
            raise UnprocessableEntity("'resourceType' should be Encounter.")
        del data['resourceType']
        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "franchise_id": franchise_id,
            "agency_id": agency_id,
            "shift_id": shift_id,
            "data": data
        }
        return make_response(
            jsonify(FhirClockInOutTranslation(**kwargs).create_clock_in()), 201
        )


class FhirClockOut(BaseFHIRView):

    def put(self, carelog_id):

        if carelog_id.isdigit():
             carelog_id = database_id_to_hash('CareLog', int(carelog_id))
        else:
             raise UnprocessableEntity("CareLog Id needs to be integer.")

        try:
            data = request.get_json(force=True)
        except BadRequest:
            raise CustomBadRequest()

        if data.get('resourceType') != 'Encounter':
            raise UnprocessableEntity("'resourceType' should be Encounter.")
        del data['resourceType']

        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "franchise_id": franchise_id,
            "agency_id": agency_id,
            "carelog_id": carelog_id,
            "data": data,
        }
        return make_response(
            jsonify(FhirClockInOutTranslation(**kwargs).create_clock_out()), 201
        )


class FhirTask(BaseFHIRView):

    def get(self, task_id=None):
        if task_id:
            return self.get_by_id(task_id)

    def get_by_id(self, task_id):
        if task_id.isdigit():
            database_id = int(task_id)
            task_id = database_id_to_hash('Task', database_id)

        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "agency_id": agency_id,
            "franchise_id": franchise_id,
            "task_id": task_id,
        }

        return jsonify(
            FhirTaskTranslation(**kwargs).get_task()
        )

    def put(self, task_id):

        if task_id.isdigit():
             task_id = database_id_to_hash('Task', int(task_id))
        else:
             raise UnprocessableEntity("Task Id needs to be integer.")

        try:
            data = request.get_json(force=True)
        except BadRequest:
            raise CustomBadRequest()

        if data.get('resourceType') != 'Task':
            raise UnprocessableEntity("'resourceType' should be Task.")
        del data['resourceType']

        agency_id = request.args.get('agency_id', request.args.get('agencyId', None)) or \
                    request.form.get('agency_id')
        franchise_id = request.args.get('franchise_id', request.args.get('franchiseId', None)) or \
                       request.form.get('franchise_id')
        kwargs = {
            "franchise_id": franchise_id,
            "agency_id": agency_id,
            "task_id": task_id,
            "data": data,
        }
        return make_response(
            jsonify(FhirTaskTranslation(**kwargs).create_clock_out()), 201
        )
