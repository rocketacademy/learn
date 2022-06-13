from django.conf import settings
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException


class Hubspot:
    def __init__(self):
        self.client = hubspot.Client.create(api_key=settings.HUBSPOT_API_KEY)

    def create_contact(self, properties):
        simple_public_object_input = SimplePublicObjectInput(properties=properties)

        try:
            api_response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )

            return api_response.to_dict()
        except ApiException as error:
            print(f'Exception when calling basic_api->create: {error}')

    def get_contact(self, contact_id):
        try:
            api_response = self.client.crm.contacts.basic_api.get_by_id(contact_id=contact_id, archived=False)

            return api_response.to_dict()
        except ApiException as error:
            print(f'Exception when calling basic_api->get_by_id: {error}')

    def update_contact(self, contact_id, properties):
        simple_public_object_input = SimplePublicObjectInput(properties=properties)

        try:
            api_response = self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=simple_public_object_input
            )

            return api_response
        except ApiException as error:
            print(f'Exception when calling basic_api->update: {error}')

def contact_requires_update(existing_user, hubspot_contact):
    if existing_user.email is not hubspot_contact['email']:
        return True
    if existing_user.first_name is not hubspot_contact['firstname']:
        return True
    if existing_user.last_name is not hubspot_contact['lastname']:
        return True
    return False
