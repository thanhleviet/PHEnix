'''Filter VCFs on AD ratio.

Created on 24 Sep 2015

@author: alex
'''

import argparse
import logging

from phe.variant_filters import PHEFilterBase


class DP4Filter(PHEFilterBase):
    '''Filter sites by AD ratio.'''


    name = "DP4"
    _default_threshold = 0.9
    parameter = "dp4_ratio"

    @classmethod
    def customize_parser(self, parser):
        arg_name = self.parameter.replace("_", "-")
        parser.add_argument("--%s" % arg_name, type=float, default=self._default_threshold,
                help="Filter sites below minimum dp4 ratio (default: %s)" % self._default_threshold)

    def __init__(self, args):
        """AD Ratio constructor."""
        # This needs to happen first, because threshold is initialised here.
        super(DP4Filter, self).__init__(args)

        # Change the threshold to custom dp value.
        self.threshold = self._default_threshold
        if isinstance(args, argparse.Namespace):
            self.threshold = args.ad_ratio
        elif isinstance(args, dict):
            try:
                self.threshold = float(args.get(self.parameter))
            except TypeError:
                logging.error("Could not retrieve threshold from %s", args.get(self.parameter))
                self.threshold = None


    def __call__(self, record):
        """Filter a :py:class:`vcf.model._Record`."""

        if not record.is_snp:
            return None

        try:
            record_dp = record.INFO.get("DP4")

            # FIXME: when record length is > 2, what do you do?
            assert len(record_dp) == 4, "DP4 data should have 4 datum POS: %i" % record.POS

            depth = sum(record_dp)

            ratio = float(sum(record_dp[2:])) / depth
        except Exception:
            logging.error("Could not calculate DP4 ratio from %s POS: %s", record_dp, record.POS)
            ratio = None

        if ratio is None or ratio < self.threshold:
            # FIXME: When ratio is None, i.e. error, what do you do?
            return ratio or False
        else:
            return None

    def short_desc(self):
        short_desc = self.__doc__ or ''

        if short_desc:
            short_desc = "%s (DP4 ratio > %s )" % (short_desc, self.threshold)

        return short_desc