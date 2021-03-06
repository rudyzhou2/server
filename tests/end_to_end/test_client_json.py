"""
Performs an end-to-end test where we verify that the data
output by the client command line interface is equal to
the values we expect using the test dataset.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import unittest

import ga4gh.client as client
import ga4gh.backend as backend
import ga4gh.cli as cli
import ga4gh.protocol as protocol
import ga4gh.datarepo as datarepo
import tests.utils as utils
import tests.paths as paths

import freezegun


@freezegun.freeze_time(datetime.datetime.now())
class TestClientOutput(unittest.TestCase):
    """
    Base class for client output tests
    """
    def setUp(self):
        self._maxDiff = None
        repoPath = paths.testDataRepo
        self._dataUrl = "file://{}".format(repoPath)
        dataRepository = datarepo.SqlDataRepository(repoPath)
        dataRepository.open(datarepo.MODE_READ)
        self._backend = backend.Backend(dataRepository)
        self._client = client.LocalClient(self._backend)

    def captureCliOutput(self, command, arguments, outputFormat):
        clientCommand = "{} {} {} -O {}".format(
            command, self._dataUrl, arguments, outputFormat)
        stdout, stderr = utils.captureOutput(
            cli.client_main, clientCommand.split())
        self.assertEqual(len(stderr), 0)
        return stdout


class TestClientFasta(TestClientOutput):
    """
    Tests client FASTA output
    """
    def captureFastaOutput(self, command, arguments=""):
        stdout = self.captureCliOutput(command, arguments, "fasta")
        lines = stdout.split()
        return lines

    def testListReferenceBases(self):
        referenceSetIterator = self._client.search_reference_sets()
        referenceSet = next(referenceSetIterator)
        referencesIterator = self._client.search_references(referenceSet.id)
        reference = next(referencesIterator)
        start = 1
        end = 5
        lines = self.captureFastaOutput(
            "references-list-bases --start {} --end {}".format(start, end),
            reference.id)
        self.assertEqual(
            lines[0], ">{}:{}-{}".format(reference.id, start, end))
        cliBases = ''.join(lines[1:])
        bases = self._client.list_reference_bases(reference.id, start, end)
        self.assertEqual(cliBases, bases)


class TestClientJson(TestClientOutput):
    """
    Tests that the JSON output by the client on the command line for
    various options is equal to the values we find using the Python
    client API.
    """
    def captureJsonOutput(self, command, arguments=""):
        """
        Runs the specified command add the JSON output option and
        returns the result as a list of JSON parsed dictionaries.
        """
        stdout = self.captureCliOutput(command, arguments, "json")
        cliOutput = []
        for line in stdout.splitlines():
            try:
                cliOutput.append(json.loads(line))
            except ValueError, e:
                raise Exception((e, line, stdout, command, arguments))
        return cliOutput

    def verifyParsedOutputsEqual(
            self, clientIterator, cliCommand, cliArguments=""):
        """
        Verify that the parsed JSON of all the objects in the specified
        client iterator are equal to the parsed JSON from the specified
        CLI command.
        """
        cliOutput = self.captureJsonOutput(cliCommand, cliArguments)
        clientOutput = [protocol.toJsonDict(gObj) for gObj in clientIterator]
        self.assertEqual(clientOutput, cliOutput)
        return len(clientOutput)

    def testGetCallSet(self):
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                for callSet in self._client.search_call_sets(variantSet.id):
                    self.verifyParsedOutputsEqual(
                        [callSet], "callsets-get", callSet.id)

    def testGetDataset(self):
        for dataset in self._client.search_datasets():
            self.verifyParsedOutputsEqual(
                [dataset], "datasets-get", dataset.id)

    def testGetReadGroup(self):
        for dataset in self._client.search_datasets():
            for readGroupSet in self._client.search_read_group_sets(
                    dataset.id):
                for readGroup in readGroupSet.read_groups:
                    self.verifyParsedOutputsEqual(
                        [readGroup], "readgroups-get", readGroup.id)

    def testGetReadGroupSet(self):
        for dataset in self._client.search_datasets():
            for readGroupSet in self._client.search_read_group_sets(
                    dataset.id):
                self.verifyParsedOutputsEqual(
                    [readGroupSet], "readgroupsets-get", readGroupSet.id)

    def testGetReference(self):
        for referenceSet in self._client.search_reference_sets():
            for reference in self._client.search_references(
                    referenceSet.id):
                self.verifyParsedOutputsEqual(
                    [reference], "references-get", reference.id)

    def testGetReferenceSet(self):
        for referenceSet in self._client.search_reference_sets():
            self.verifyParsedOutputsEqual(
                [referenceSet], "referencesets-get", referenceSet.id)

    @unittest.skip("TODO: clarify semantics of callsets and fix")
    def testGetVariant(self):
        test_executed = 0
        start = 0
        end = 1000
        referenceName = "1"
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                variants = self._client.search_variants(
                    variantSet.id, start=start, end=end,
                    reference_name=referenceName)
                for variant in variants:
                    test_executed += self.verifyParsedOutputsEqual(
                        [variant], "variants-get", variant.id)
        self.assertGreater(test_executed, 0)

    def testGetVariantAnnotationSet(self):
        # TODO this doesn't actually test get_variant_annotation_set
        test_executed = 0
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                for annSet in self._client.search_variant_annotation_sets(
                        variantSet.id):
                    test_executed += self.verifyParsedOutputsEqual(
                        [annSet], "variantannotationsets-get", annSet.id)
        self.assertGreater(test_executed, 0)

    def testGetVariantSet(self):
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                self.verifyParsedOutputsEqual(
                    [variantSet], "variantsets-get", variantSet.id)

    def testSearchCallSets(self):
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                iterator = self._client.search_call_sets(variantSet.id)
                args = "--variantSetId {}".format(variantSet.id)
                self.verifyParsedOutputsEqual(
                    iterator, "callsets-search", args)

    def testGetBioSamples(self):
        for dataset in self._client.search_datasets():
            for bioSample in self._client.search_bio_samples(dataset.id):
                self.verifyParsedOutputsEqual(
                    [bioSample], "biosamples-get", bioSample.id)

    def testGetIndividuals(self):
        for dataset in self._client.search_datasets():
            for individual in self._client.search_individuals(dataset.id):
                self.verifyParsedOutputsEqual(
                    [individual], "individuals-get", individual.id)

    def testSearchDatasets(self):
        iterator = self._client.search_datasets()
        self.verifyParsedOutputsEqual(iterator, "datasets-search")

    def testSearchReadGroupSets(self):
        for dataset in self._client.search_datasets():
            iterator = self._client.search_read_group_sets(dataset.id)
            self.verifyParsedOutputsEqual(
                iterator, "readgroupsets-search",
                "--datasetId {}".format(dataset.id))
            for readGroupSet in iterator:
                bioIterator = self._client.search_read_group_sets(
                    dataset.id,
                    name=readGroupSet.name,
                    bio_sample_id=readGroupSet.bioSampleId)
                self.verifyParsedOutputsEqual(
                    bioIterator, "readgroupsets-search",
                    "--datasetId {} --name {} --bioSampleId {}".format(
                        dataset.id,
                        readGroupSet.name,
                        readGroupSet.bioSampleId))

    def testSearchReads(self):
        test_executed = 0
        start = 0
        end = 1000000
        for dataset in self._client.search_datasets():
            for readGroupSet in self._client.search_read_group_sets(
                    dataset.id):
                for readGroup in readGroupSet.read_groups:
                    reference = self._client.search_references(
                        reference_set_id=readGroup.reference_set_id).next()
                    referenceId = reference.id
                    iterator = self._client.search_reads(
                        [readGroup.id], reference_id=referenceId,
                        start=start, end=end)
                    args = "--start {} --end {} --readGroupIds {}\
                    --referenceId {}".format(
                        start, end, readGroup.id, referenceId)
                    test_executed += self.verifyParsedOutputsEqual(
                        iterator, "reads-search", args)
        self.assertGreater(test_executed, 0)

    def testSearchReferenceSets(self):
        iterator = self._client.search_reference_sets()
        self.verifyParsedOutputsEqual(iterator, "referencesets-search")

    def testSearchReferences(self):
        for referenceSet in self._client.search_reference_sets():
            iterator = self._client.search_references(
                reference_set_id=referenceSet.id)
            args = "--referenceSetId={}".format(referenceSet.id)
            self.verifyParsedOutputsEqual(iterator, "references-search", args)

    def testSearchVariantSets(self):
        for dataset in self._client.search_datasets():
            iterator = self._client.search_variant_sets(dataset.id)
            self.verifyParsedOutputsEqual(iterator, "variantsets-search")

    def testSearchVariants(self):
        test_executed = 0
        start = 0
        end = 1000
        referenceName = "1"
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                iterator = self._client.search_variants(
                    variantSet.id, start=start, end=end,
                    reference_name=referenceName, call_set_ids=[])
                args = "--variantSetId {} --start {} --end {} -r {}".format(
                    variantSet.id, start, end, referenceName)
                test_executed += self.verifyParsedOutputsEqual(
                    iterator, "variants-search", args)
        self.assertGreater(test_executed, 0)

    def testSearchBioSamples(self):
        for dataset in self._client.search_datasets():
            iterator = self._client.search_bio_samples(dataset.id)
            self.verifyParsedOutputsEqual(iterator, "biosamples-search")
        for dataset in self._client.search_datasets():
            for bioSample in self._client.search_bio_samples(dataset.id):
                iterator = self._client.search_bio_samples(
                    dataset.id, bioSample.name)
                self.verifyParsedOutputsEqual(
                    iterator,
                    "biosamples-search",
                    "--datasetId {} --name {}".format(
                        dataset.id,
                        bioSample.name))
                if bioSample.individualId:
                    iterator = self._client.search_bio_samples(
                        dataset.id, individual_id=bioSample.individualId)
                    self.verifyParsedOutputsEqual(
                        iterator,
                        "biosamples-search",
                        "--datasetId {} --individualId {}".format(
                            dataset.id,
                            bioSample.individualId))

    def testSearchIndividuals(self):
        for dataset in self._client.search_datasets():
            iterator = self._client.search_individuals(dataset.id)
            self.verifyParsedOutputsEqual(iterator, "individuals-search")
        for dataset in self._client.search_datasets():
            for individual in self._client.search_individuals(dataset.id):
                iterator = self._client.search_individuals(
                    dataset.id, individual.name)
                self.verifyParsedOutputsEqual(
                    iterator, "individuals-search", "--name {}".format(
                        individual.name))

    def testSearchVariantAnnotationSets(self):
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                iterator = self._client.search_variant_annotation_sets(
                    variantSet.id)
                args = "{}".format(variantSet.id)
                self.verifyParsedOutputsEqual(
                    iterator, "variantannotationsets-search", args)

    def testSearchVariantAnnotations(self):
        test_executed = 0
        start = 0
        end = 10000000
        referenceName = "1"
        for dataset in self._client.search_datasets():
            for variantSet in self._client.search_variant_sets(dataset.id):
                searchIterator = self._client.search_variant_annotation_sets(
                    variantSet.id)
                for variantAnnotationSet in searchIterator:
                    iterator = self._client.search_variant_annotations(
                        variantAnnotationSet.id,
                        start=start,
                        end=end,
                        reference_name=referenceName)
                    args = ("--variantAnnotationSetId {}"
                            " --start {} --end {} -r {}").format(
                        variantAnnotationSet.id, start, end, referenceName)
                    test_executed += self.verifyParsedOutputsEqual(
                        iterator, "variantannotations-search", args)
        self.assertGreater(test_executed, 0)

    # def testGetFeatures(self):  # TODO

    # def testSearchFeatures(self):  # TODO

    # def testGetFeatureSets(self):  # TODO

    # def testSearchFeatureSets(self):  # TODO
