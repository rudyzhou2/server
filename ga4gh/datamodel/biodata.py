"""
Dataset objects
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import ga4gh.datamodel as datamodel
import ga4gh.protocol as protocol


class AbstractBioSample(datamodel.DatamodelObject):
    compoundIdClass = datamodel.BioSampleCompoundId
    def __init__(self, parentContainer, localId):
        super(AbstractBioSample, self).__init__(parentContainer, localId)
        self._createDateTime = datetime.datetime.now().isoformat()
        self._updateDateTime = datetime.datetime.now().isoformat()
        self._description = ""
        self._disease = None
        self._info = {}
        self._name = localId

    def toProtocolElement(self):
        bioSample = protocol.BioSample()
        bioSample.createDateTime = self.getCreateDateTime()
        bioSample.description = self.getDescription()
        bioSample.disease = self.getDisease()
        bioSample.id = self.getId()
        bioSample.info = self.getInfo()
        bioSample.name = self.getName()
        bioSample.updateDateTime = self.getUpdateDateTime()
        return bioSample

    def getCreateDateTime(self):
        return self._createDateTime

    def getUpdateDateTime(self):
        return self._updateDateTime

    def getDescription(self):
        return self._description

    def getDisease(self):
        return self._disease

    def getInfo(self):
        return self._info

    def getName(self):
        return self._name

class JsonBioSample(AbstractBioSample, datamodel.MetadataSidecarMixin):
    def __init__(self, parentContainer, localId, filepath):
        super(JsonBioSample, self).__init__(parentContainer, localId)
        self.loadSidecar(filepath)

    def getCreateDateTime(self):
        if self.sidecar('createDateTime'):
            return self.sidecar('createDateTime')
        else:
            return self._createDateTime

    def getUpdateDateTime(self):
        if self.sidecar('updateDateTime'):
            return self.sidecar('updateDateTime')
        else:
            return self._updateDateTime

    def getDescription(self):
        if self.sidecar('description'):
            return self.sidecar('description')
        else:
            return self._description

    def getDisease(self):
        if self.sidecar('disease'):
            return self.sidecar('disease')
        else:
            return self._disease

    def getInfo(self):
        if self.sidecar('info'):
            return self.sidecar('info')
        else:
            return self._info

    def getName(self):
        if self.sidecar('name'):
            return self.sidecar('name')
        else:
            return self._name