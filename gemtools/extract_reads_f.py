import os
import csv
import gzip
import sys
import time
from itertools import izip_longest, islice
import io

def extract_reads(**kwargs):	

	if 'read1' in kwargs:
		r1 = kwargs['read1']
	if 'read2' in kwargs:
		r2 = kwargs['read2']
	if 'index1' in kwargs:
		i1 = kwargs['index1']	
	if 'bcs' in kwargs:
		bc_file = kwargs['bcs']
	if 'fq_outdir' in kwargs:
		out_dir = kwargs['fq_outdir']
	
	if not out_dir.endswith("/"):
		out_dir = out_dir + "/"
	
	out_r1 = str(out_dir) + str(r1.split("/")[-1])
	out_r2 = str(out_dir) + str(r2.split("/")[-1])
	out_i1 = str(out_dir) + str(i1.split("/")[-1])
	
	if os.path.isfile(out_r1):
		print str(out_r1) + " already exists"
		sys.exit()
	
	if os.path.isfile(out_r2):
		print str(out_r2) + " already exists"
		sys.exit()

	if os.path.isfile(out_i1):
		print str(out_i1) + " already exists"
		sys.exit()

	if not os.path.isdir(out_dir):
		os.makedirs(out_dir)
	
	out_r1_file = gzip.open(out_r1,'w')
	out_r2_file = gzip.open(out_r2,'w')
	out_si_file = gzip.open(out_i1,'w')

	bcs_list = []
	with open(bc_file,'r') as f:
		for line in csv.reader(f,delimiter='\t'):
			bcs_list.append(line[0])

	bcs_set = set(bcs_list)
	bcs_set = [b.split("-")[0] for b in bcs_set]

	n = 0
	i = 0

	with io.BufferedReader(gzip.open(r1, 'r')) as f1, io.BufferedReader(gzip.open(r2, 'r')) as f2, io.BufferedReader(gzip.open(i1,'r')) as ind:
		cur_time = time.time()
		while True:
			lines_r1 = list(islice(f1,4))
			lines_r2 = list(islice(f2,4))
			lines_index = list(islice(ind,4))

			if not lines_r1:
				break

			n = n + 1
			if (n % 1000000 == 0):
				print >>sys.stderr, "%d reads processed, %d records matched bcs in a %d second chunk" % (n, i, time.time() - cur_time)
				cur_time = time.time()

			if (lines_r1[1][0:16] in bcs_set):
				i = i + 1

				for line in lines_r1:
					out_r1_file.write(line)
				for line in lines_r2:
					out_r2_file.write(line)
				for line in lines_index:
					out_si_file.write(line)
