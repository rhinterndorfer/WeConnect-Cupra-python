import logging
import json
import requests

from weconnect_cupra.addressable import AddressableObject, ChangeableAttribute
from weconnect_cupra.elements.control_operation import ControlOperation
from weconnect_cupra.api.cupra.elements.charging_settings import ChargingSettings
from weconnect_cupra.api.cupra.elements.climatization_settings import ClimatizationSettings
from weconnect_cupra.elements.error import Error
from weconnect_cupra.errors import ControlError, SetterError
from weconnect_cupra.util import celsiusToKelvin, farenheitToKelvin
from weconnect_cupra.api.vw.domain import Domain

LOG = logging.getLogger("weconnect_cupra")


class Controls(AddressableObject):
    def __init__(
        self,
        localAddress,
        vehicle,
        parent,
    ):
        self.vehicle = vehicle
        super().__init__(localAddress=localAddress, parent=parent)
        self.update()

        # Public API properties
        self.climatizationControl = None
        self.chargingControl = None
        self.wakeupControl = ChangeableAttribute(
            localAddress='wakeup', parent=self, value=ControlOperation.NONE, valueType=ControlOperation, valueSetter=self.__setWakeupControlChange)

    def update(self):
        for domain in self.vehicle.domains.values():
            for status in domain.values():
                if isinstance(status, ClimatizationSettings):
                    if self.climatizationControl is None:
                        self.climatizationControl = ChangeableAttribute(
                            localAddress='climatisation', parent=self, value=ControlOperation.NONE, valueType=(ControlOperation, float),
                            valueSetter=self.__setClimatizationControlChange)
                elif isinstance(status, ChargingSettings):
                    if self.chargingControl is None:
                        self.chargingControl = ChangeableAttribute(
                            localAddress='charging', parent=self, value=ControlOperation.NONE, valueType=ControlOperation,
                            valueSetter=self.__setChargingControlChange)

    def __setClimatizationControlChange(self, value):  # noqa: C901
        if isinstance(value, ControlOperation):
            if value not in [ControlOperation.START, ControlOperation.STOP]:
                raise ControlError('Could not control climatisation, control operation %s cannot be executed', value)
            control = value
            temperature = None
        elif isinstance(value, (int, float)):
            control = ControlOperation.START
            temperature = float(value)
        else:
            raise ControlError('Could not control climatisation, control argument %s cannot be understood', value)

        if control == ControlOperation.START:
            # Build up settings dict
            settingsDict = dict()
            if control == ControlOperation.START:
                if 'climatisation' not in self.vehicle.domains and 'climatisationSettings' not in self.vehicle.domains['climatisation']:
                    raise ControlError('Could not control climatisation, there are no climatisationSettings for the vehicle available.')
                climatizationSettings = self.vehicle.domains['climatisation']['climatisationSettings']
                for child in climatizationSettings.getLeafChildren():
                    if isinstance(child, ChangeableAttribute):
                        settingsDict[child.getLocalAddress()] = child.value
                if temperature is not None:
                    if 'targetTemperature_C' in settingsDict:
                        settingsDict['targetTemperature_C'] = temperature
                    settingsDict['targetTemperature_K'] = celsiusToKelvin(temperature)
                elif 'targetTemperature_K' not in settingsDict:
                    if 'targetTemperature_C' in settingsDict:
                        settingsDict['targetTemperature_K'] = celsiusToKelvin(settingsDict['targetTemperature_C'])
                    elif 'targetTemperature_F' in settingsDict:
                        settingsDict['targetTemperature_K'] = farenheitToKelvin(settingsDict['targetTemperature_F'])
                    else:
                        settingsDict['targetTemperature_K'] = celsiusToKelvin(20.5)

            # Do API request to set temperature
            data = json.dumps(settingsDict)
            controlResponse = self.vehicle.fetcher.put(
                url=f'https://ola.prod.code.seat.cloud.vwgroup.com/v1/vehicles/{self.vehicle.vin.value}/climatisation/requests/settings',
                data=data,
                allow_redirects=True,
                headers={
                    "accept": '*/*',
                    "user-agent": "CUPRAApp%20-%20Store/20220207 CFNetwork/1240.0.4 Darwin/20.6.0",
                    "Content-Type": "application/json",
                    "accept-language": "de-de",
                    "Accept-Encoding": "gzip, deflate"
                } )
            if controlResponse.status_code != requests.codes['ok']:
                errorDict = controlResponse.json()
                if errorDict is not None and 'error' in errorDict:
                    error = Error(localAddress='error', parent=self, fromDict=errorDict['error'])
                    if error is not None:
                        message = ''
                        if error.message.enabled and error.message.value is not None:
                            message += error.message.value
                        if error.info.enabled and error.info.value is not None:
                            message += ' - ' + error.info.value
                        if error.retry.enabled and error.retry.value is not None:
                            if error.retry.value:
                                message += ' - Please retry in a moment'
                            else:
                                message += ' - No retry possible'
                        raise SetterError(f'Could not control climatisation ({message})')
                    else:
                        raise SetterError(f'Could not control climatisation ({controlResponse.status_code})')
                raise SetterError(f'Could not control climatisation ({controlResponse.status_code})')

        # Do API request to set run state
        controlResponse = self.vehicle.fetcher.post(
            url=f'https://ola.prod.code.seat.cloud.vwgroup.com/vehicles/{self.vehicle.vin.value}/climatisation/requests/{control.value}',
            allow_redirects=True,
            headers={
                "accept": '*/*',
                "user-agent": "CUPRAApp%20-%20Store/20220207 CFNetwork/1240.0.4 Darwin/20.6.0",
                "Content-Type": "application/json",
                "accept-language": "de-de",
                "Accept-Encoding": "gzip, deflate"
            } )
        if controlResponse.status_code != requests.codes['ok']:
            errorDict = controlResponse.json()
            if errorDict is not None and 'error' in errorDict:
                error = Error(localAddress='error', parent=self, fromDict=errorDict['error'])
                if error is not None:
                    message = ''
                    if error.message.enabled and error.message.value is not None:
                        message += error.message.value
                    if error.info.enabled and error.info.value is not None:
                        message += ' - ' + error.info.value
                    if error.retry.enabled and error.retry.value is not None:
                        if error.retry.value:
                            message += ' - Please retry in a moment'
                        else:
                            message += ' - No retry possible'
                    raise SetterError(f'Could not control climatisation ({message})')
                else:
                    raise SetterError(f'Could not control climatisation ({controlResponse.status_code})')
            raise SetterError(f'Could not control climatisation ({controlResponse.status_code})')

        # Build up response
        responseDict = controlResponse.json()
        if 'data' in responseDict and 'requestID' in responseDict['data']:
            if self.vehicle.requestTracker is not None:
                self.vehicle.requestTracker.trackRequest(responseDict['data']['requestID'], Domain.CLIMATISATION, 20, 120)

    def __setChargingControlChange(self, value):  # noqa: C901
        # Validate inputs
        if value not in [ControlOperation.START, ControlOperation.STOP]:
            return
        
        # Do API request
        controlResponse = self.vehicle.fetcher.post(
            url=f'https://ola.prod.code.seat.cloud.vwgroup.com/vehicles/{self.vehicle.vin.value}/charging/requests/{value.value}',
            allow_redirects=True,
            headers={
                "accept": '*/*',
                "user-agent": "CUPRAApp%20-%20Store/20220207 CFNetwork/1240.0.4 Darwin/20.6.0",
                "Content-Type": "application/json",
                "accept-language": "de-de",
                "Accept-Encoding": "gzip, deflate"
            } )
        # Handle response
        if controlResponse.status_code != requests.codes['ok']:
            errorDict = controlResponse.json()
            if errorDict is not None and 'error' in errorDict:
                error = Error(localAddress='error', parent=self, fromDict=errorDict['error'])
                if error is not None:
                    message = ''
                    if error.message.enabled and error.message.value is not None:
                        message += error.message.value
                    if error.info.enabled and error.info.value is not None:
                        message += ' - ' + error.info.value
                    if error.retry.enabled and error.retry.value is not None:
                        if error.retry.value:
                            message += ' - Please retry in a moment'
                        else:
                            message += ' - No retry possible'
                    raise SetterError(f'Could not control charging ({message})')
                else:
                    raise SetterError(f'Could not control charging ({controlResponse.status_code})')
            raise SetterError(f'Could not control charging ({controlResponse.status_code})')

        # Maybe send response to request tracker
        responseDict = controlResponse.json()
        if 'data' in responseDict and 'requestID' in responseDict['data']:
            if self.vehicle.requestTracker is not None:
                self.vehicle.requestTracker.trackRequest(responseDict['data']['requestID'], Domain.CHARGING, 20, 120)

    def __setWakeupControlChange(self, value):  # noqa: C901
        if value in [ControlOperation.START]:
            url = f'https://mobileapi.apps.emea.vwapps.io/vehicles/{self.vehicle.vin.value}/vehiclewakeuptrigger'

            controlResponse = self.vehicle.weConnect.session.post(url, data='{}', allow_redirects=True)

            if controlResponse.status_code not in (requests.codes['ok'], requests.codes['no_content']):
                errorDict = controlResponse.json()
                if errorDict is not None and 'error' in errorDict:
                    error = Error(localAddress='error', parent=self, fromDict=errorDict['error'])
                    if error is not None:
                        message = ''
                        if error.message.enabled and error.message.value is not None:
                            message += error.message.value
                        if error.info.enabled and error.info.value is not None:
                            message += ' - ' + error.info.value
                        if error.retry.enabled and error.retry.value is not None:
                            if error.retry.value:
                                message += ' - Please retry in a moment'
                            else:
                                message += ' - No retry possible'
                        raise SetterError(f'Could not control wakeup ({message})')
                    else:
                        raise SetterError(f'Could not control wakeup ({controlResponse.status_code})')
                raise SetterError(f'Could not control wakeup ({controlResponse.status_code})')
