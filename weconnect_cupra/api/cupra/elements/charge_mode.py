from enum import Enum
from typing import List
import logging

from weconnect_cupra.addressable import AddressableObject, ChangeableAttribute, AddressableLeaf
#from weconnect_cupra.elements.generic_status import GenericStatus
from weconnect_cupra.api.cupra.elements.generic_settings import GenericSettings
from weconnect_cupra.api.cupra.elements.enums import ChargeModeState

LOG = logging.getLogger("weconnect_cupra")


class ChargeMode(GenericSettings):
    def __init__(
        self,
        vehicle,
        parent,
        statusId,
        fromDict=None,
        fixAPI=True,
    ):
        
        self.preferredChargeMode = ChangeableAttribute(localAddress='preferredChargeMode'
                                                        , value=None, parent=self
                                                        , valueType=ChargeModeState)
        self.availableChargeModes = ChargeMode.ChargeModeList(localAddress='availableChargeModes', parent=self)
        super().__init__(vehicle=vehicle, parent=parent, statusId=statusId, fromDict=fromDict, fixAPI=fixAPI)
        self.api_version = 'v1/'
        self.action_value = 'modes'
        self.root_element_name = ''


        self.preferredChargeMode.addObserver(self.valueChanged, AddressableLeaf.ObserverEvent.VALUE_CHANGED,
                                       priority=AddressableLeaf.ObserverPriority.INTERNAL_MID)

    def update(self, fromDict, ignoreAttributes=None):
        ignoreAttributes = ignoreAttributes or []
        LOG.debug('Update ChargeMode status from dict')

        if 'preferredChargeMode' in fromDict:
            self.preferredChargeMode.fromDict(fromDict, 'preferredChargeMode')

            if 'availableChargeModes' in fromDict:
                if self.availableChargeModes is None:
                    self.availableChargeModes = ChargeMode.ChargeModeList(localAddress='availableChargeModes', parent=self,
                                                                          fromDict=fromDict['availableChargeModes'])
                else:
                    self.availableChargeModes.update(fromDict=fromDict['availableChargeModes'])
            elif self.availableChargeModes is not None:
                self.availableChargeModes.clear()
                self.availableChargeModes.enabled = False
        else:
            self.preferredChargeMode.enabled = False
            self.availableChargeModes.clear()
            self.availableChargeModes.enabled = False

        super().update(fromDict=fromDict, ignoreAttributes=(
            ignoreAttributes + ['preferredChargeMode', 'availableChargeModes']))

    def __str__(self):
        string = super().__str__()
        if self.preferredChargeMode is not None and self.preferredChargeMode.enabled:
            string += f'\n\tPreferred charge mode: {self.preferredChargeMode.value.value}'  # pylint: disable=no-member
        if self.availableChargeModes is not None and self.availableChargeModes.enabled:
            string += f'\n\tAvailable charge modes: {self.availableChargeModes}'
        return string

    

    class ChargeModeList(AddressableObject, List):
        def update(self, fromDict):
            LOG.debug('Update timer from dict')

            self.clear()
            if fromDict is not None and len(fromDict) > 0:
                for mode in fromDict:
                    try:
                        self.append(ChargeModeState(mode))
                    except ValueError:
                        self.append(ChargeModeState.UNKNOWN)
                        LOG.warning('An unsupported mode: %s was provided, please report this as a bug', mode)
                if not self.enabled:
                    self.enabled = True
            elif self.enabled:
                self.enabled = False

        def __str__(self):
            return '[' + ', '.join([item.value for item in self]) + ']'
