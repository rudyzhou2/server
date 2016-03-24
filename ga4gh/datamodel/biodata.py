"""
Biodata objects
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import ga4gh.datamodel as datamodel
import ga4gh.protocol as protocol
import ga4gh.exceptions as exceptions


class AbstractBioSample(datamodel.DatamodelObject):
    """
    This class represents an abstract BioSample object.
    It sets default values and getters, as well as the
    toProtocolElement function.
    """
    compoundIdClass = datamodel.BioSampleCompoundId

    def __init__(self, parentContainer, localId, individualName=None):
        super(AbstractBioSample, self).__init__(parentContainer, localId)
        self._createDateTime = datetime.datetime.now().isoformat()
        self._updateDateTime = datetime.datetime.now().isoformat()
        self._description = ""
        self._disease = None
        self._info = {}
        self._name = localId
        self._individualName = individualName
        self._individualId = None

    def toProtocolElement(self):
        bioSample = protocol.BioSample()
        bioSample.createDateTime = self.getCreateDateTime()
        bioSample.description = self.getDescription()
        bioSample.disease = self.getDisease()
        bioSample.id = self.getId()
        bioSample.individualId = self.getIndividualId()
        bioSample.info = self.getInfo()
        bioSample.name = self.getName()
        bioSample.updateDateTime = self.getUpdateDateTime()
        return bioSample

    def getIndividualId(self):
        """
        Return a string identifier using the datasetId
        and localId. LocalIds of individuals are expected
        to have the same localId as a BioSample.
        :return:
        """
        datasetId = self.getParentContainer().getCompoundId()
        compoundId = datamodel.IndividualCompoundId(
            datasetId, self._individualName)
        return str(compoundId)

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
    """
    Allows a BioSample object to be populated using JSON
    metadata information by passing a filepath during
    instantiation.
    b = JsonBioSample(dataset, name, filepath)
    """
    def __init__(self, parentContainer, localId, filePath):
        super(JsonBioSample, self).__init__(parentContainer, localId)
        self._filePath = filePath
        self.loadSidecar(filePath)
        self.validate()

    def validate(self):
        if not protocol.BioSample.validate(
                self.toProtocolElement().toJsonDict()):
            raise exceptions.FileOpenFailedException(self._filePath)

    def _getField(self, fieldName):
        if self.sidecar(fieldName):
            return self.sidecar(fieldName)
        else:
            return self.__getattribute__('_' + fieldName)

    def getIndividualId(self):
        return self._getField('individualId')

    def getCreateDateTime(self):
        return self._getField('createDateTime')

    def getUpdateDateTime(self):
        return self._getField('updateDateTime')

    def getDescription(self):
        return self._getField('description')

    def getDisease(self):
        return self._getField('disease')

    def getInfo(self):
        return self._getField('info')

    def getName(self):
        return self._getField('name')


class AbstractIndividual(datamodel.DatamodelObject):
    """
    This class represents an abstract Individual object.
    It sets default values and getters, as well as the
    toProtocolElement function.
    """
    compoundIdClass = datamodel.IndividualCompoundId

    def __init__(self, parentContainer, localId):
        super(AbstractIndividual, self).__init__(parentContainer, localId)
        self._createDateTime = datetime.datetime.now().isoformat()
        self._updateDateTime = datetime.datetime.now().isoformat()
        self._description = ""
        self._species = None
        self._sex = None
        self._info = {}
        self._name = localId

    def toProtocolElement(self):
        gaIndividual = protocol.Individual()
        gaIndividual.createDateTime = self.getCreateDateTime()
        gaIndividual.updateDateTime = self.getUpdateDateTime()
        gaIndividual.description = self.getDescription()
        gaIndividual.species = self.getSpecies()
        gaIndividual.sex = self.getSex()
        gaIndividual.id = self.getId()
        gaIndividual.info = self.getInfo()
        gaIndividual.name = self.getName()
        return gaIndividual

    def getCreateDateTime(self):
        return self._createDateTime

    def getUpdateDateTime(self):
        return self._updateDateTime

    def getDescription(self):
        return self._description

    def getSpecies(self):
        return self._species

    def getSex(self):
        return self._sex

    def getInfo(self):
        return self._info

    def getName(self):
        return self._name


class JsonIndividual(AbstractIndividual, datamodel.MetadataSidecarMixin):
    """
    Allows a Individual object to be populated using JSON
    metadata information by passing a filepath during
    instantiation.
    b = JsonIndividual(dataset, name, filepath)
    """
    def __init__(self, parentContainer, localId, filePath):
        super(JsonIndividual, self).__init__(parentContainer, localId)
        self._filePath = filePath
        self.loadSidecar(filePath)
        self.validate()

    def validate(self):
        if not protocol.Individual.validate(
                self.toProtocolElement().toJsonDict()):
            raise exceptions.FileOpenFailedException(self._filePath)

    def _getField(self, fieldName):
        if self.sidecar(fieldName):
            return self.sidecar(fieldName)
        else:
            return self.__getattribute__('_' + fieldName)

    def getCreateDateTime(self):
        return self._getField('createDateTime')

    def getUpdateDateTime(self):
        return self._getField('updateDateTime')

    def getDescription(self):
        return self._getField('description')

    def getSpecies(self):
        species = self._getField('species')
        if species:
            species = protocol.OntologyTerm().fromJsonDict(
                self._getField('species'))
        return species

    def getSex(self):
        sex = self._getField('sex')
        if sex:
            sex = protocol.OntologyTerm().fromJsonDict(
                self._getField('sex'))
        return sex

    def getInfo(self):
        return self._getField('info')

    def getName(self):
        return self._getField('name')
