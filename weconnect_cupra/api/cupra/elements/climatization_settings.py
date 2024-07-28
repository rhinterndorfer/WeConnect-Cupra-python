from enum import Enum
import logging

from weconnect_cupra.addressable import AddressableLeaf, ChangeableAttribute, AddressableAttribute, AliasChangeableAttribute
from weconnect_cupra.api.cupra.elements.generic_settings import GenericSettings
from weconnect_cupra.util import celsiusToKelvin, farenheitToKelvin, kelvinToCelsius, kelvinToFarenheit

LOG = logging.getLogger("weconnect_cupra")


class ClimatizationSettings(GenericSettings):
    def __init__(
        self,
        vehicle,
        parent,
        statusId,
        fromDict=None,
        fixAPI=True,
    ):
        self.targetTemperature_K = ChangeableAttribute(
            localAddress='targetTemperature_K', parent=self, value=None, valueType=float)
        self.targetTemperature_C = AliasChangeableAttribute(localAddress='targetTemperatureInCelsius', parent=self, value=None,
                                                            targetAttribute=self.targetTemperature_K, conversion=celsiusToKelvin, valueType=float)
        self.targetTemperature_F = AliasChangeableAttribute(localAddress='targetTemperatureInFahrenheit', parent=self, value=None,
                                                            targetAttribute=self.targetTemperature_K, conversion=farenheitToKelvin, valueType=float)
        self.unitInCar = AddressableAttribute(
            localAddress='unitInCar', parent=self, value=None, valueType=ClimatizationSettings.UnitInCar)
        self.climatisationWithoutExternalPower = ChangeableAttribute(
            localAddress='climatisationWithoutExternalPower', parent=self, value=None, valueType=bool)
        self.climatisationAtUnlock = ChangeableAttribute(
            localAddress='climatisationAtUnlock', parent=self, value=None, valueType=bool)
        self.windowHeatingEnabled = ChangeableAttribute(
            localAddress='windowHeatingEnabled', parent=self, value=None, valueType=bool)
        self.zoneFrontLeftEnabled = ChangeableAttribute(
            localAddress='zoneFrontLeftEnabled', parent=self, value=None, valueType=bool)
        self.zoneFrontRightEnabled = ChangeableAttribute(
            localAddress='zoneFrontRightEnabled', parent=self, value=None, valueType=bool)
        self.zoneRearLeftEnabled = ChangeableAttribute(
            localAddress='zoneRearLeftEnabled', parent=self, value=None, valueType=bool)
        self.zoneRearRightEnabled = ChangeableAttribute(
            localAddress='zoneRearRightEnabled', parent=self, value=None, valueType=bool)
        super().__init__(vehicle=vehicle, parent=parent, statusId=statusId, fromDict=fromDict, fixAPI=fixAPI)

        self.targetTemperature_K.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.climatisationWithoutExternalPower.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.climatisationAtUnlock.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.windowHeatingEnabled.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.zoneFrontLeftEnabled.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.zoneFrontRightEnabled.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.zoneRearLeftEnabled.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)
        self.zoneRearRightEnabled.addObserver(
            self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
            priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)

    def update(self, fromDict, ignoreAttributes=None):  # noqa: C901
        ignoreAttributes = ignoreAttributes or []
        LOG.debug('Update Climatization settings from dict')

        # Cupra
        if 'value' not in fromDict:
            fromDict['value'] = fromDict
        # if 'targetTemperature_C' not in fromDict['value']:
        #     fromDict['value']['targetTemperature_C'] = kelvinToCelsius(fromDict['value']['targetTemperature_K'])
        # if 'targetTemperature_F' not in fromDict['value']:
        #     fromDict['value']['targetTemperature_F'] = kelvinToFarenheit(fromDict['value']['targetTemperature_K'])

        if 'value' in fromDict:
            self.targetTemperature_K.fromDict(fromDict['value'], 'targetTemperature_K')
            self.targetTemperature_C.fromDict(fromDict['value'], 'targetTemperatureInCelsius')
            self.targetTemperature_F.fromDict(fromDict['value'], 'targetTemperatureInFahrenheit')
            self.unitInCar.fromDict(fromDict['value'], 'unitInCar')
            self.climatisationWithoutExternalPower.fromDict(fromDict['value'], 'climatisationWithoutExternalPower')
            self.climatisationAtUnlock.fromDict(fromDict['value'], 'climatisationAtUnlock')
            self.windowHeatingEnabled.fromDict(fromDict['value'], 'windowHeatingEnabled')
            self.zoneFrontLeftEnabled.fromDict(fromDict['value'], 'zoneFrontLeftEnabled')
            self.zoneFrontRightEnabled.fromDict(fromDict['value'], 'zoneFrontRightEnabled')
            self.zoneRearLeftEnabled.fromDict(fromDict['value'], 'zoneRearLeftEnabled')
            self.zoneRearRightEnabled.fromDict(fromDict['value'], 'zoneRearRightEnabled')
        else:
            self.targetTemperature_K.enabled = False
            self.targetTemperature_C.enabled = False
            self.targetTemperature_F.enabled = False
            self.unitInCar.enabled = False
            self.climatisationWithoutExternalPower.enabled = False
            self.climatisationAtUnlock.enabled = False
            self.windowHeatingEnabled.enabled = False
            self.zoneFrontLeftEnabled.enabled = False
            self.zoneFrontRightEnabled.enabled = False
            self.zoneRearLeftEnabled.enabled = False
            self.zoneRearRightEnabled.enabled = False

        super().update(fromDict=fromDict, ignoreAttributes=(ignoreAttributes + [
            'targetTemperature_K',
            'targetTemperatureInCelsius',
            'targetTemperatureInFahrenheit',
            'unitInCar',
            'climatisationWithoutExternalPower',
            'climatisationAtUnlock',
            'windowHeatingEnabled',
            'zoneFrontLeftEnabled',
            'zoneFrontRightEnabled',
            'zoneRearLeftEnabled',
            'zoneRearRightEnabled']))

    def __str__(self):  # noqa: C901
        string = super().__str__()
        if self.targetTemperature_C.enabled:
            string += f'\n\tTarget Temperature in °C: {self.targetTemperature_C.value} °C '
        if self.targetTemperature_F.enabled:
            string += f'\n\tTarget Temperature in °F: {self.targetTemperature_F.value} °F '
        if self.targetTemperature_K.enabled:
            string += f'\n\tTarget Temperature in °K: {self.targetTemperature_K.value} °K '
        if self.unitInCar.enabled:
            string += f'\n\tTemperature unit in car: {self.unitInCar.value.value}'
        if self.climatisationWithoutExternalPower.enabled:
            string += f'\n\tClimatization without external Power: {self.climatisationWithoutExternalPower.value}'
        if self.climatisationAtUnlock.enabled:
            string += f'\n\tStart climatization after unlock: {self.climatisationAtUnlock.value}'
        if self.windowHeatingEnabled.enabled:
            string += f'\n\tWindow heating: {self.windowHeatingEnabled.value}'
        if self.zoneFrontLeftEnabled.enabled:
            string += f'\n\tHeating Front Left Seat: {self.zoneFrontLeftEnabled.value}'
        if self.zoneFrontRightEnabled.enabled:
            string += f'\n\tHeating Front Right Seat: {self.zoneFrontRightEnabled.value}'
        if self.zoneRearLeftEnabled.enabled:
            string += f'\n\tHeating Rear Left Seat: {self.zoneRearLeftEnabled.value}'
        if self.zoneRearRightEnabled.enabled:
            string += f'\n\tHeating Rear Right Seat: {self.zoneRearRightEnabled.value}'
        return string

    class UnitInCar(Enum,):
        CELSIUS = 'celsius'
        FARENHEIT = 'farenheit'
        UNKNOWN = 'unknown unit'
