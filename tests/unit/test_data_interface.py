"""
Tests the data interfacing layer for various objects
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import ga4gh.client as client
import ga4gh.datarepo as datarepo
import ga4gh.backend as backend
import tests.paths as paths
import tests.utils as utils


class TestInterfacingLayer(unittest.TestCase):
    """
    Test fetching objects via the db and via the client return
    identical results
    """
    def _assertEqual(self, dbObj, pbObj):
        dbToPb = dbObj.toProtocolElement()
        self.assertEqual(dbToPb, pbObj)

    def _getPageSizes(self, num):
        if num <= 0:
            return []
        return [None, 1, 2, 3, num - 1, num, num + 1]

    def _testGetMethod(self, repoIteratorMethod, clientGetMethod):
        repoObjs = repoIteratorMethod()
        for repoObj in repoObjs:
            id_ = repoObj.getId()
            clientObj = clientGetMethod(id_)
            self._assertEqual(repoObj, clientObj)

    def _testSearchMethod(self, repoIteratorMethod, clientSearchMethod):
        repoObjs = list(repoIteratorMethod())
        numRepoObjs = len(repoObjs)
        pageSizes = self._getPageSizes(numRepoObjs)
        for pageSize in pageSizes:
            self._client.set_page_size(pageSize)
            clientObjs = list(clientSearchMethod())
            for repoObj, clientObj in utils.zipLists(repoObjs, clientObjs):
                self._assertEqual(repoObj, clientObj)

    def _testSearchMethodInContainer(
            self, containerAccessorMethod, clientSearchMethod,
            containerIteratorMethod):
        for container in containerIteratorMethod:
            containerId = container.getId()
            repoObjs = getattr(container, containerAccessorMethod)()
            numRepoObjs = len(repoObjs)
            pageSizes = self._getPageSizes(numRepoObjs)
            for pageSize in pageSizes:
                self._client.set_page_size(pageSize)
                clientObjs = list(clientSearchMethod(containerId))
                for repoObj, clientObj in utils.zipLists(
                        repoObjs, clientObjs):
                    self._assertEqual(repoObj, clientObj)

    def setUp(self):
        self._repo = datarepo.SqlDataRepository(paths.testDataRepo)
        self._repo.open(datarepo.MODE_READ)
        self._backend = backend.Backend(self._repo)
        self._client = client.LocalClient(self._backend)

    def testGetBioSample(self):
        self._testGetMethod(
            self._repo.allBioSamples, self._client.get_bio_sample)

    def testGetIndividual(self):
        self._testGetMethod(
            self._repo.allIndividuals, self._client.get_individual)

    def testGetDataset(self):
        self._testGetMethod(
            self._repo.getDatasets, self._client.get_dataset)

    def testGetReadGroupSet(self):
        self._testGetMethod(
            self._repo.allReadGroupSets, self._client.get_read_group_set)

    def testGetReadGroup(self):
        self._testGetMethod(
            self._repo.allReadGroups, self._client.get_read_group)

    def testGetCallSet(self):
        self._testGetMethod(
            self._repo.allCallSets, self._client.get_call_set)

    def testGetVariant(self):
        repoVariantSets = self._repo.allVariantSets()
        referenceName = self._repo.getReferenceSets(
            )[0].getReferences()[0].getName()
        for variantSet in repoVariantSets:
            repoVariants = variantSet.getVariants(referenceName, 0, 2**32)
            for repoVariant in repoVariants:
                variantId = repoVariant.getId()
                variant = self._client.get_variant(variantId)
                self._assertEqual(repoVariant, variant)

    def testGetVariantSet(self):
        self._testGetMethod(
            self._repo.allVariantSets, self._client.get_variant_set)

    def testGetVariantAnnotationSet(self):
        self._testGetMethod(
            self._repo.allVariantAnnotationSets,
            self._client.get_variant_annotation_set)

    def testGetFeatureSet(self):
        self._testGetMethod(
            self._repo.allFeatureSets, self._client.get_feature_set)

    def testGetFeature(self):
        repoFeatures = self._repo.allFeatures()
        for repoFeature in repoFeatures:
            repoFeature = repoFeature[0]
            featureId = repoFeature.id
            feature = self._client.get_feature(featureId)
            self.assertEqual(repoFeature, feature)

    def testGetReferenceSet(self):
        self._testGetMethod(
            self._repo.getReferenceSets, self._client.get_reference_set)

    def testGetReference(self):
        self._testGetMethod(
            self._repo.allReferences, self._client.get_reference)

    def testSearchVariants(self):
        for variantSet in self._repo.allVariantSets():
            referenceSet = variantSet.getReferenceSet()
            referenceName = referenceSet.getLocalId()
            variantSetId = variantSet.getId()
            repoVariants = list(
                variantSet.getVariants(referenceName, 0, 2**32))
            numRepoVariants = len(repoVariants)
            pageSizes = self._getPageSizes(numRepoVariants)
            for pageSize in pageSizes:
                self._client.set_page_size(pageSize)
                variants = self._client.search_variants(variantSetId)
                for repoVariant, variant in utils.zipLists(
                        repoVariants, variants):
                    self._assertEqual(repoVariant, variant)

    def testSearchVariantAnnotations(self):
        for variantAnnotationSet in self._repo.allVariantAnnotationSets():
            variantAnnotationSetId = variantAnnotationSet.getId()
            variantSet = variantAnnotationSet._parentContainer
            referenceSet = variantSet.getReferenceSet()
            referenceName = referenceSet.getLocalId()
            repoVariantAnnotations = list(
                variantAnnotationSet.getVariantAnnotations(
                    referenceName, 0, 2**32))
            numRepoVariantAnnotations = len(repoVariantAnnotations)
            pageSizes = self._getPageSizes(numRepoVariantAnnotations)
            for pageSize in pageSizes:
                self._client.set_page_size(pageSize)
                variantAnnotations = self._client.search_variant_annotations(
                    variantAnnotationSetId, referenceName=referenceName)
                for repoVa, va in utils.zipLists(
                        repoVariantAnnotations, variantAnnotations):
                    self._assertEqual(repoVa, va)

    # TODO
    """
    # something is wrong with the features generator...
    # doesn't always set nextPageToken appropriately?
    def testSearchFeatures(self):
        repoFeatureSets = self._repo.allFeatureSets()
        for repoFeatureSet in repoFeatureSets:
            repoFeatures = list(repoFeatureSet.getFeatures())
            numFeatures = len(repoFeatures)
            featureSetId = repoFeatureSet.getId()
            pageSizes = self._getPageSizes(numFeatures)
            for pageSize in pageSizes:
                features = list(self._client.search_features(featureSetId))
                for repoFeature, feature in utils.zipLists(
                        repoFeatures, features):
                    repoFeature = repoFeature[0]
                    self.assertEqual(repoFeature, feature)
    """

    def testSearchDatasets(self):
        self._testSearchMethod(
            self._repo.getDatasets, self._client.search_datasets)

    def testSearchVariantSets(self):
        self._testSearchMethodInContainer(
            'getVariantSets',
            self._client.search_variant_sets,
            self._repo.getDatasets())

    def testSearchVariantAnnotationSets(self):
        self._testSearchMethodInContainer(
            'getVariantAnnotationSets',
            self._client.search_variant_annotation_sets,
            self._repo.allVariantSets())

    def testSearchFeatureSets(self):
        self._testSearchMethodInContainer(
            'getFeatureSets',
            self._client.search_feature_sets,
            self._repo.getDatasets())

    def testSearchCallSets(self):
        self._testSearchMethodInContainer(
            'getCallSets',
            self._client.search_call_sets,
            self._repo.allVariantSets())

    def testSearchBioSamples(self):
        self._testSearchMethodInContainer(
            'getBioSamples',
            self._client.search_bio_samples,
            self._repo.getDatasets())

    def testSearchIndividuals(self):
        self._testSearchMethodInContainer(
            'getIndividuals',
            self._client.search_individuals,
            self._repo.getDatasets())

    def testSearchReadGroupSets(self):
        self._testSearchMethodInContainer(
            'getReadGroupSets',
            self._client.search_read_group_sets,
            self._repo.getDatasets())

    def testSearchReads(self):
        for repoReadGroup in self._repo.allReadGroups():
            repoReferenceSet = \
                repoReadGroup._parentContainer.getReferenceSet()
            for repoReference in repoReferenceSet.getReferences():
                referenceId = repoReference.getId()
                readGroupId = repoReadGroup.getId()
                repoReads = list(
                    repoReadGroup.getReadAlignments(repoReference))
                numRepoReads = len(repoReads)
                pageSizes = self._getPageSizes(numRepoReads)
                for pageSize in pageSizes:
                    self._client.set_page_size(pageSize)
                    reads = list(self._client.search_reads(
                        [readGroupId], referenceId))
                    for repoRead, read in utils.zipLists(
                            repoReads, reads):
                        self.assertEqual(repoRead, read)

    def testSearchReferenceSets(self):
        self._testSearchMethod(
            self._repo.getReferenceSets, self._client.search_reference_sets)

    def testSearchReferences(self):
        repoReferenceSets = self._repo.getReferenceSets()
        for repoReferenceSet in repoReferenceSets:
            referenceSetId = repoReferenceSet.getId()
            repoReferences = repoReferenceSet.getReferences()
            numRefs = len(repoReferences)
            pageSizes = self._getPageSizes(numRefs)
            for pageSize in pageSizes:
                self._client.set_page_size(pageSize)
                references = list(
                    self._client.search_references(referenceSetId))
                for repoReference, reference in utils.zipLists(
                        repoReferences, references):
                    self._assertEqual(repoReference, reference)
