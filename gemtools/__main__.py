#!/usr/bin/env python


"""
gemtools version %version
Copyright (C) 2018 Stephanie Greer <sgreer2@stanford.edu>
gemtools is a suite of tools to work with linked read sequencing data.
Usage:
    gemtools -T TOOL [options] [-o output]
"""

import os
import sys
from optparse import OptionParser, OptionGroup

from gemtools import __version__
from gemtools.bedpe2window_f import bedpe2window
from gemtools.get_shared_bcs_f import get_shared_bcs
from gemtools.assign_sv_haps_f import assign_sv_haps
from gemtools.count_bcs_f import count_bcs
from gemtools.get_phased_basic_f import get_phased_basic
from gemtools.get_phase_blocks_f import get_phase_blocks
from gemtools.get_bcs_in_region_f import get_bcs_in_region
from gemtools.get_phased_bcs_f import get_phased_bcs
from gemtools.select_bcs_f import select_bcs
from gemtools.count_bcs_list_f import count_bcs_list
from gemtools.plot_hmw_f import plot_hmw
from gemtools.extract_reads_interleaved_f import extract_reads_interleaved
from gemtools.extract_reads_separate_f import extract_reads_separate
from gemtools.get_hmw_summary_f import get_hmw_summary


class GemtoolsOptionParser(OptionParser):
	def get_usage(self):
		return self.usage.lstrip().replace('%version', __version__)
	def error(self, msg):
		print('Run "gemtools --help" to see command-line options.')
		self.exit(2, "\n%s: error: %s\n" % (self.get_prog_name(), msg))

class CommandLineError(Exception):
	pass

def get_option_parser():
	parser = GemtoolsOptionParser(usage=__doc__, version=__version__)
	
	parser.add_option("-T", "--tool", default=None, dest="tool",
		help="Name of tool to use ")
	parser.add_option("-o", "--output", metavar="FILE",
		dest="outfile",
		help="Name of output file")

	group = OptionGroup(parser, "Input files")
	group.add_option("-i", "--input", metavar="FILE",
		dest="infile",
		help="Name of input file ")
	group.add_option("-b","--bam", metavar="FILE",
		dest="bam",
		help="bam file")
	group.add_option("-v","--vcf", metavar="FILE",
		dest="vcf",
		help="vcf file")
	group.add_option("-c","--vcf_control", metavar="FILE",
		dest="vcf_control",
		help="Control vcf file")
	group.add_option("-t","--vcf_test", metavar="FILE",
		dest="vcf_test",
		help="Test vcf file")
	parser.add_option_group(group)	
	
	group = OptionGroup(parser, "Windows")
	group.add_option("-w", "--window", type=int, default=50000,
		dest="window_size", metavar="WINDOW",
		help="Size of window to create around bkpts in bp      "
			"default: 50000")
	group.add_option("-x","--in_window", type=int, default=1000,
		dest="in_window",metavar="WINDOW",
		help="Size of small windows in bp                       "
			"default: 1000")
	group.add_option("-y","--out_window", type=int, default=50000,
		dest="out_window",metavar="WINDOW",
		help="Size of large window in bp                       "
			"default: 50000")
	parser.add_option_group(group)

	group = OptionGroup(parser, "Regions")
	group.add_option("-f","--region_in",
		dest="region_in", metavar='REGION',
		help="In region(s) in format: "
		"chr1,1000000,2000000 or "
		"chr1,1000000,2000000;chr2:3000000,4000000")
	group.add_option("-g","--region_out",
		dest="region_out", metavar='REGION',
		help="Out region(s) in format: "
		"chr1,1000000,2000000 or "
		"chr1,1000000,2000000;chr2:3000000,4000000")
	parser.add_option_group(group)

	group = OptionGroup(parser, "Barcodes")
	group.add_option("-l","--bc_list", metavar="FILE",
		dest="bcs",
		help="File with list of barcodes")			
	group.add_option("-q","--bc_select",metavar='(all|shared)',
		dest="bc_select",choices=('all', 'shared'), default="shared",
		help="BCs to consider: all bcs or shared bcs               "
			"default: shared")
	parser.add_option_group(group)

	group = OptionGroup(parser, "Specifics")
	group.add_option("-n","--chrom", metavar="CHR",
		dest="chrom",
		help="Chromosome number; ex: 'chr22','22'")
	group.add_option("-p","--phase_block",
		dest="phase_block", metavar="PHASE_ID",
		help="Phase block id (from vcf)")
	group.add_option("-s","--sv_name",
		dest="sv_name", metavar="SV",
		help="Name of SV; ex: 'call_144', '144'")
	parser.add_option_group(group)

	group = OptionGroup(parser, "Fastq")
	group.add_option("-d","--fqdir",
		dest="fqdir", metavar="FQ_DIR",
		help="Long Rnager fastq directory")
	group.add_option("-j","--sample_bcs",
		dest="s_bcs", metavar="SAMPLE_BCS",
		help="Sample barcodes")
	group.add_option("-k","--lanes",
		dest="lanes", metavar="LANES",
		help="Numbers of sequencing lanes; ex: '1,5'")
	group.add_option("-z","--outdir",
		dest="outdir", metavar="OUT_DIR",
		help="Name of output directory")
	group.add_option("-m","--read1",
		dest="read1", metavar="READ1",
		help="read1 fastq file")
	group.add_option("-u","--read2",
		dest="read2", metavar="READ2",
		help="read2 fastq file")
	group.add_option("-r","--index1",
		dest="index1", metavar="INDEX1",
		help="index1 fastq file")
	parser.add_option_group(group)

	return parser

def pipeline_from_parsed_args(options):
	if options.tool=="bedpe2window":
		pipeline = bedpe2window(bedpe=options.infile, window=options.window_size, out=options.outfile)
	if options.tool=="get_shared_bcs":
		pipeline = get_shared_bcs(sv=options.infile, bam=options.bam, out=options.outfile)
	if options.tool=="assign_sv_haps":
		pipeline = assign_sv_haps(sv=options.infile, vcf_control=options.vcf_control, vcf_test=options.vcf_test, out=options.outfile)
	if options.tool=="count_bcs":
		pipeline = count_bcs(bam=options.bam, sv=options.infile, in_window=options.in_window, out_window=options.out_window, sv_name=options.sv_name, bcs=options.bc_select, out=options.outfile)
	if options.tool=="get_phased_basic":
		pipeline = get_phased_basic(vcf=options.vcf, out=options.outfile, chrom=options.chrom)
	if options.tool=="get_phase_blocks":
		pipeline = get_phase_blocks(infile_basic=options.infile, out=options.outfile)
	if options.tool=="get_phased_bcs":
		pipeline = get_phased_bcs(infile_basic=options.infile, ps=options.phase_block, out=options.outfile)
	if options.tool=="select_bcs":
		pipeline = select_bcs(region_in=options.region_in, region_out=options.region_out, bam=options.bam, out=options.outfile)
	if options.tool=="count_bcs_list":
		pipeline = count_bcs_list(region=options.region_in, in_window=options.in_window, bam=options.bam, bcs=options.bcs, out=options.outfile)
	if options.tool=="get_bcs_in_region":
		pipeline = get_bcs_in_region(region=options.region_in,bam=options.bam, out=options.outfile)
	if options.tool=="plot_hmw":
		pipeline = plot_hmw(in_windows=options.infile, out=options.outfile)
	if options.tool=="extract_reads_interleaved":
		pipeline = extract_reads_interleaved(fqdir=options.fqdir, s_bcs=options.s_bcs, lanes=options.lanes, bcs=options.bcs, fq_outdir=options.outdir)
	if options.tool=="extract_reads_separate":
		pipeline = extract_reads_separate(bcs=options.bcs, fq_outdir=options.outdir, read1=options.read1, read2=options.read2, index1=options.index1)
	return pipeline

def main(cmdlineargs=None):
	parser = get_option_parser()
	if cmdlineargs is None:
		cmdlineargs = sys.argv[1:]
	options, args = parser.parse_args(args=cmdlineargs)
	
	if not options.tool:
		parser.error("Must provide a tool to run with -T")
		
	if options.tool=="bedpe2window":
		print "gemtools -T bedpe2window -i [LR_input.bedpe] -w [window_size] -o [out.bedpe]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		
		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")
		if str(options.window_size).isdigit() and int(options.window_size)>0:
			print "window_size: " + str(options.window_size)
		else:
			parser.error(str(options.window_size) + " must be an integer >0")
	
	if options.tool=="get_shared_bcs":
		print "gemtools -T get_shared_bcs -i [out.bedpe] -b [LR_bam_file] -o [out.shared]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.bam:
			parser.error('bam file is required')

		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")
		if os.path.isfile(options.bam):
			print "input file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not exist")
		if str(options.bam).endswith(".bam"):
			print "Bam file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not appear to be a bam file")

	if options.tool=="assign_sv_haps":
		print "gemtools -T assign_sv_haps -i [out.shared] -c [LR_control.vcf.gz] -t [LR_test.vcf.gz] -o [out.haps]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.vcf_control:
			parser.error('Control vcf file is required')
		if not options.vcf_test:
			parser.error('Test vcf file is required')

		if str(options.vcf_control).endswith(".vcf.gz"):
			print "Control vcf file: " + str(options.vcf_control)
		else:
			parser.error(str(options.vcf_control) + " does not appear to be a gzipped vcf file")		
		if str(options.vcf_test).endswith(".vcf.gz"):
			print "Test vcf file: " + str(options.vcf_test)
		else:
			parser.error(str(options.vcf_test) + " does not appear to be a gzipped vcf file")

	if options.tool=="count_bcs":
		print "gemtools -T count_bcs -i [out.shared] -b [LR.bam] -x [in_window] -y [out_window] -s [sv_name] -q [all|shared] -o [out.bc_count]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.sv_name:
			parser.error('SV name is required')
		if not options.bam:
			parser.error('bam file is required')

		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")
		if str(options.in_window).isdigit() and int(options.in_window)>0:
			print "In window size: " + str(options.in_window)
		else:
			parser.error(str(options.in_window) + " must be an integer >0")
		if str(options.out_window).isdigit() and int(options.out_window)>0:
			print "Out window size: " + str(options.out_window)
		else:
			parser.error(str(options.out_window) + " must be an integer >0")
		if str(options.bam).endswith(".bam"):
			print "Bam file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not appear to be a bam file")

	if options.tool=="get_phased_basic":
		print "gemtools -T get_phased_basic -v [LR.vcf.gz] -o [output.phased_basic] -n [chr_num]"
		if not options.outfile:
			parser.error('Output file is required')
		if not options.vcf:
			parser.error('vcf file is required')

		if str(options.vcf).endswith(".vcf.gz"):
			print "vcf file: " + str(options.vcf)
		else:
			parser.error(str(options.vcf) + " does not appear to be a gzipped vcf file")
	
	if options.tool=="get_phase_blocks":
		print "gemtools -T get_phase_blocks -i [out.phased_basic] -o [out.phase_blocks]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')

		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")

	if options.tool=="get_bcs_in_region":
		print "gemtools -T get_bcs_in_region -b [LR.bam] -f [region_in] -o [out.bcs]"
		if not options.outfile:
			parser.error('Output file is required')
		if not options.bam:
			parser.error('bam file is required')
		if not options.region_in:
			parser.error('Need to specify region')
		
		if str(options.bam).endswith(".bam"):
			print "Bam file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not appear to be a bam file")
	
	if options.tool=="get_phased_bcs":
		print "gemtools -T get_phased_bcs -i [out.phased_basic] -p [phase_block_id] -o [out.phased_bcs]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.phase_block:
			parser.error('Phase block ID is required')

		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")

	if options.tool=="select_bcs":
		print "gemtools -T select_bcs -b [LR.bam] -f [region_in] -g [region_out] -o [out.bcs]"
		if not options.bam:
			parser.error('bam file is required')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.region_in:
			parser.error('Need to specify region in')
		if not options.region_out:
			parser.error('Need to specify region out')
			
		if str(options.bam).endswith(".bam"):
			print "Bam file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not appear to be a bam file")

	if options.tool=="count_bcs_list":
		print "gemtools -T count_bcs_list -b [LR.bam] -f [region_in] -x [in_window] -b [bc_list] -o [out.bc_count]"
		if not options.bam:
			parser.error('bam file is required')
		if not options.region_in:
			parser.error('Need to specify region in')
		if not options.outfile:
			parser.error('Output file is required')
		if not options.bcs:
			parser.error('Barcodes file is required')

		if str(options.bam).endswith(".bam"):
			print "Bam file: " + str(options.bam)
		else:
			parser.error(str(options.bam) + " does not appear to be a bam file")
		if str(options.in_window).isdigit() and int(options.in_window)>0:
			print "In window size: " + str(options.in_window)
		else:
			parser.error(str(options.in_window) + " must be an integer >0")
		if os.path.isfile(options.bcs):
			print "bcs file: " + str(options.bcs)
		else:
			parser.error(str(options.bcs) + " does not exist")

	if options.tool=="plot_hmw":
		print "gemtools -T plot_hmw -i [out.bc_count] -o [out.pdf]"
		if not options.infile:
			parser.error('Input file is required')
		if not options.outfile:
			parser.error('Output file is required')
		
		if os.path.isfile(options.infile):
			print "input file: " + str(options.infile)
		else:
			parser.error(str(options.infile) + " does not exist")

	if options.tool=="extract_reads_interleaved":
		if not options.fqdir:
			parser.error('Fastq dir is required')
		if not options.s_bcs:
			parser.error('Sample barcodes are required')
		if not options.lanes:
			parser.error('Sample lanes are required')
		if not options.bcs:
			parser.error('Droplet barcodes are required')
		
		if os.path.isfile(options.bcs):
			print "bcs file: " + str(options.bcs)
		else:
			parser.error(str(options.bcs) + " does not exist")
	
	if options.tool=="extract_reads_separate":
		if not options.bcs:
			parser.error('Droplet barcodes are required')
		if not options.read1:
			parser.error('Read1 file is required')
		if not options.read2:
			parser.error('Read2 file is required')
		if not options.index1:
			parser.error('Index1 file is required')
			
		if os.path.isfile(options.bcs):
			print "bcs file: " + str(options.bcs)
		else:
			parser.error(str(options.bcs) + " does not exist")
		
	
	pipeline = pipeline_from_parsed_args(options)
	runner = pipeline

if __name__ == '__main__':
	main()
