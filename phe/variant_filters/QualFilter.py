'''Filter VCF on GQ parameter.
Created on 24 Sep 2015

@author: alex
'''

import argparse
import logging

from phe.variant_filters import PHEFilterBase


class QualFilter(PHEFilterBase):
    '''Filter sites by QUAL score.'''

    name = "LowSNPQual"
    _default_threshold = 40.0
    parameter = "qual_score"

    @classmethod
    def customize_parser(self, parser):
        arg_name = self.parameter.replace("_", "-")
        parser.add_argument("--%s" % arg_name, type=float, default=self._default_threshold,
                help="Filter sites below given GQ score (default: %s)" % self._default_threshold)

    def __init__(self, args):
        """Min Depth constructor."""
        # This needs to happen first, because threshold is initialised here.
        super(QualFilter, self).__init__(args)

        # Change the threshold to custom gq value.
        self.threshold = self._default_threshold
        if isinstance(args, argparse.Namespace):
            self.threshold = args.gq_score
        elif isinstance(args, dict):
            try:
                self.threshold = float(args.get(self.parameter))
            except TypeError:
                logging.error("Could not retrieve threshold from %s", args.get(self.parameter))
                self.threshold = None

    def __call__(self, record):
        """Filter a :py:class:`vcf.model._Record`."""


        record_qual = record.QUAL

        if record_qual is None or record_qual < self.threshold:
            # FIXME: when record_gq is None, i,e, error, what do you do?
            return record_qual or False
        else:
            return None

    def short_desc(self):
        short_desc = self.__doc__ or ''

        if short_desc:
            short_desc = "%s (QUAL > %s)" % (short_desc, self.threshold)

        return short_desc