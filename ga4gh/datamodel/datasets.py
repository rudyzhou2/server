"""
Dataset objects
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ga4gh.datamodel as datamodel
import ga4gh.datamodel.reads as reads
import ga4gh.datamodel.sequenceAnnotations as sequenceAnnotations
import ga4gh.datamodel.variants as variants
import ga4gh.exceptions as exceptions
import ga4gh.protocol as protocol
import ga4gh.datamodel.bio_metadata as biodata
from ga4gh import pb


class Dataset(datamodel.DatamodelObject):
    """
    The base class of datasets containing variants and reads
    """
    compoundIdClass = datamodel.DatasetCompoundId

    def __init__(self, localId):
        super(Dataset, self).__init__(None, localId)
        self._description = None
        self._variantSetIds = []
        self._variantSetIdMap = {}
        self._variantSetNameMap = {}
        self._featureSetIds = []
        self._featureSetIdMap = {}
        self._featureSetNameMap = {}
        self._readGroupSetIds = []
        self._readGroupSetIdMap = {}
        self._readGroupSetNameMap = {}
        self._bioSampleIds = []
        self._bioSampleIdMap = {}
        self._bioSampleNameMap = {}
        self._individualIds = []
        self._individualIdMap = {}
        self._individualNameMap = {}

    def populateFromRow(self, row):
        """
        Populates the instance variables of this Dataset from the
        specified database row.
        """
        self._description = row[b'description']

    def setDescription(self, description):
        """
        Sets the description for this dataset to the specified value.
        """
        self._description = description

    def addVariantSet(self, variantSet):
        """
        Adds the specified variantSet to this dataset.
        """
        id_ = variantSet.getId()
        self._variantSetIdMap[id_] = variantSet
        self._variantSetNameMap[variantSet.getLocalId()] = variantSet
        self._variantSetIds.append(id_)

    def addBioSample(self, bioSample):
        """
        Adds the specified bioSample to this dataset.
        """
        id_ = bioSample.getId()
        self._bioSampleIdMap[id_] = bioSample
        self._bioSampleIds.append(id_)
        self._bioSampleNameMap[bioSample.getName()] = bioSample

    def addIndividual(self, individual):
        """
        Adds the specified individual to this dataset.
        """
        id_ = individual.getId()
        self._individualIdMap[id_] = individual
        self._individualIds.append(id_)
        self._individualNameMap[individual.getName()] = individual

    def addFeatureSet(self, featureSet):
        """
        Adds the specified variantSet to this dataset.
        """
        id_ = featureSet.getId()
        self._featureSetIdMap[id_] = featureSet
        self._featureSetIds.append(id_)
        name = featureSet.getLocalId()
        self._featureSetNameMap[name] = featureSet

    def addReadGroupSet(self, readGroupSet):
        """
        Adds the specified readGroupSet to this dataset.
        """
        id_ = readGroupSet.getId()
        self._readGroupSetIdMap[id_] = readGroupSet
        self._readGroupSetNameMap[readGroupSet.getLocalId()] = readGroupSet
        self._readGroupSetIds.append(id_)

    def toProtocolElement(self):
        dataset = protocol.Dataset()
        dataset.id = self.getId()
        dataset.name = pb.string(self.getLocalId())
        dataset.description = pb.string(self.getDescription())
        return dataset

    def getVariantSets(self):
        """
        Returns the list of VariantSets in this dataset
        """
        return [self._variantSetIdMap[id_] for id_ in self._variantSetIds]

    def getNumVariantSets(self):
        """
        Returns the number of variant sets in this dataset.
        """
        return len(self._variantSetIds)

    def getVariantSet(self, id_):
        """
        Returns the VariantSet with the specified name, or raises a
        VariantSetNotFoundException otherwise.
        """
        if id_ not in self._variantSetIdMap:
            raise exceptions.VariantSetNotFoundException(id_)
        return self._variantSetIdMap[id_]

    def getVariantSetByIndex(self, index):
        """
        Returns the variant set at the specified index in this dataset.
        """
        return self._variantSetIdMap[self._variantSetIds[index]]

    def getVariantSetByName(self, name):
        """
        Returns a VariantSet with the specified name, or raises a
        VariantSetNameNotFoundException if it does not exist.
        """
        if name not in self._variantSetNameMap:
            raise exceptions.VariantSetNameNotFoundException(name)
        return self._variantSetNameMap[name]

    def getFeatureSets(self):
        """
        Returns the list of FeatureSets in this dataset
        """
        return [self._featureSetIdMap[id_] for id_ in self._featureSetIds]

    def getNumFeatureSets(self):
        """
        Returns the number of feature sets in this dataset.
        """
        return len(self._featureSetIds)

    def getFeatureSet(self, id_):
        """
        Returns the FeatureSet with the specified id, or raises a
        FeatureSetNotFoundException otherwise.
        """
        if id_ not in self._featureSetIdMap:
            raise exceptions.FeatureSetNotFoundException(id_)
        return self._featureSetIdMap[id_]

    def getFeatureSetByName(self, name):
        """
        Returns the FeatureSet with the specified name, or raises
        an exception otherwise.
        """
        if name not in self._featureSetNameMap:
            raise exceptions.FeatureSetNameNotFoundException(name)
        return self._featureSetNameMap[name]

    def getFeatureSetByIndex(self, index):
        """
        Returns the feature set at the specified index in this dataset.
        """
        return self._featureSetIdMap[self._featureSetIds[index]]

    def getNumBioSamples(self):
        """
        Returns the number of biosamples sets in this dataset.
        """
        return len(self._bioSampleIds)

    def getBioSamples(self):
        """
        Returns the list of biosamples in this dataset
        """
        return [self._bioSampleIdMap[id_] for id_ in self._bioSampleIds]

    def getBioSampleByName(self, name):
        """
        Returns a BioSample with the specified name, or raises a
        BioSampleNameNotFoundException if it does not exist.
        """
        if name not in self._bioSampleNameMap:
            raise exceptions.BioSampleNameNotFoundException(name)
        return self._bioSampleNameMap[name]

    def getBioSampleByIndex(self, index):
        """
        Returns the biosample at the specified index in this dataset.
        """
        return self._bioSampleIdMap[self._bioSampleIds[index]]

    def getBioSample(self, id_):
        """
        Returns the BioSample with the specified id, or raises
        a BioSampleNotFoundException otherwise.
        """
        if id_ not in self._bioSampleIdMap:
            raise exceptions.BioSampleNotFoundException(id_)
        return self._bioSampleIdMap[id_]

    def getNumIndividuals(self):
        """
        Returns the number of individuals sets in this dataset.
        """
        return len(self._individualIds)

    def getIndividuals(self):
        """
        Returns the list of individuals in this dataset
        """
        return [self._individualIdMap[id_] for id_ in self._individualIds]

    def getIndividualByName(self, name):
        """
        Returns an individual with the specified name, or raises a
        IndividualNameNotFoundException if it does not exist.
        """
        if name not in self._individualNameMap:
            raise exceptions.IndividualNameNotFoundException(name)
        return self._individualNameMap[name]

    def getIndividualByIndex(self, index):
        """
        Returns the individual at the specified index in this dataset.
        """
        return self._individualIdMap[self._individualIds[index]]

    def getIndividual(self, id_):
        """
        Returns the Individual with the specified id, or raises
        a IndividualNotFoundException otherwise.
        """
        if id_ not in self._individualIdMap:
            raise exceptions.IndividualNotFoundException(id_)
        return self._individualIdMap[id_]

    def getNumReadGroupSets(self):
        """
        Returns the number of readgroup sets in this dataset.
        """
        return len(self._readGroupSetIds)

    def getReadGroupSets(self):
        """
        Returns the list of ReadGroupSets in this dataset
        """
        return [self._readGroupSetIdMap[id_] for id_ in self._readGroupSetIds]

    def getReadGroupSetByName(self, name):
        """
        Returns a ReadGroupSet with the specified name, or raises a
        ReadGroupSetNameNotFoundException if it does not exist.
        """
        if name not in self._readGroupSetNameMap:
            raise exceptions.ReadGroupSetNameNotFoundException(name)
        return self._readGroupSetNameMap[name]

    def getReadGroupSetByIndex(self, index):
        """
        Returns the readgroup set at the specified index in this dataset.
        """
        return self._readGroupSetIdMap[self._readGroupSetIds[index]]

    def getReadGroupSet(self, id_):
        """
        Returns the ReadGroupSet with the specified name, or raises
        a ReadGroupSetNotFoundException otherwise.
        """
        if id_ not in self._readGroupSetIdMap:
            raise exceptions.ReadGroupNotFoundException(id_)
        return self._readGroupSetIdMap[id_]

    def getDescription(self):
        """
        Returns the free text description of this dataset.
        """
        return self._description


class SimulatedDataset(Dataset):
    """
    A simulated dataset
    """
    def __init__(
            self, localId, referenceSet, randomSeed=0,
            numVariantSets=1, numCalls=1, variantDensity=0.5,
            numReadGroupSets=1, numReadGroupsPerReadGroupSet=1,
            numAlignments=1, numFeatureSets=1):
        super(SimulatedDataset, self).__init__(localId)
        self._description = "Simulated dataset {}".format(localId)
        # TODO create a simulated Ontology
        # Variants
        for i in range(numVariantSets):
            localId = "simVs{}".format(i)
            seed = randomSeed + i
            variantSet = variants.SimulatedVariantSet(
                self, referenceSet, localId, seed, numCalls, variantDensity)
            callSets = variantSet.getCallSets()
            # Add biosamples
            for callSet in callSets:
                bioSample = biodata.BioSample(
                    self, callSet.getLocalId())
                bioSample2 = biodata.BioSample(
                    self, callSet.getLocalId() + "2")
                individual = biodata.Individual(
                    self, callSet.getLocalId())
                bioSample.setIndividualId(individual.getId())
                bioSample2.setIndividualId(individual.getId())
                self.addIndividual(individual)
                self.addBioSample(bioSample)
                self.addBioSample(bioSample2)
            self.addVariantSet(variantSet)
            variantAnnotationSet = variants.SimulatedVariantAnnotationSet(
                variantSet, "simVas{}".format(i), seed)
            variantSet.addVariantAnnotationSet(variantAnnotationSet)
        # Reads
        for i in range(numReadGroupSets):
            localId = 'simRgs{}'.format(i)
            seed = randomSeed + i
            readGroupSet = reads.SimulatedReadGroupSet(
                self, localId, referenceSet, seed,
                numReadGroupsPerReadGroupSet, numAlignments)
            for rg in readGroupSet.getReadGroups():
                bioSample = biodata.BioSample(
                    self, rg.getLocalId())
                individual = biodata.Individual(
                    self, rg.getLocalId())
                bioSample.setIndividualId(individual.getId())
                rg.setBioSampleId(bioSample.getId())
                self.addIndividual(individual)
                self.addBioSample(bioSample)
            self.addReadGroupSet(readGroupSet)
        # Features
        for i in range(numFeatureSets):
            localId = "simFs{}".format(i)
            seed = randomSeed + i
            featureSet = sequenceAnnotations.SimulatedFeatureSet(
                self, localId, seed)
            featureSet.setReferenceSet(referenceSet)
            self.addFeatureSet(featureSet)
