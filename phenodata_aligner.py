from __future__ import division

import sys
import re
import csv
import argparse

from collections import OrderedDict




def pheno_to_list(pheno_file, skip_header=True):
    '''
    Function to fix phenodata of GEO datasets that
    differing numbers of columns. The input should be
    a csv with all the relevant metadata.

    By defualt, the first line is assumed to be
    the header and is skipped. Set skip_header to
    false to turn this off.
    '''
    with open(pheno_file, 'rU') as f:

        if skip_header:
            next(f)
        pheno_list = []
        for line in f:
            cur_row = []
            for meta_val in line.split(','): # splits and removes extra '
                fixed_meta_val = re.sub('\"', '', meta_val)
                cur_row.append(fixed_meta_val)
            pheno_list.append(cur_row)
        return pheno_list

def header_maker(pheno_list, delim=':'):
    '''
    This just finds the first row which has values
    in all columns and returns that as the new header
    '''

    header_list = []
    header_list.append('sampleID')
    #header_dict = OrderedDict()
    #header_dict['sampleID'] = []
    #head_str = 'sampleID,'
    for cur_row in pheno_list:
        if cur_row.count('') == 0:
            for cur_val in cur_row[1:]:
                cur_field = re.sub(' ', '_', cur_val.split(delim)[0])
                header_list.append(cur_field)
                #head_str = head_str + cur_field + ','
                #header_dict[cur_field] = []
            return header_list
            #return header_dict
            #return(head_str.strip(','))

def proper_aligner(pheno_list, delim=':'):
    '''
    This takes each list item (in this case, the rows from pheno csv)
    and puts it into a dict for each row. It then makes a new list
    for each row using the formatted headers as a key for the row
    dict. If not found, the value NA is used as a placeholder.

    The output is a list with the first item as the header and each
    subsequent item as the rows. The values are aligned using NA.
    '''
    #header_dict = header_maker(pheno_list, delim=delim)
    header_list = header_maker(pheno_list, delim=delim)
    out_list = []
    out_list.append(header_list)
    for cur_row in pheno_list:
        row_dict = {}
        row_dict['sampleID'] = cur_row[0]
        row_list = []
        for cur_val in cur_row[1:]:
            try:
                field, value = cur_val.split(delim)
                row_dict[re.sub(' ', '_', field)] = value.strip(' ')
            except ValueError:
                continue

        #for header_field in header_dict.keys():
        for header_field in header_list:
            try:
                found_value = row_dict[header_field]
                row_list.append(found_value)
            except KeyError:
                row_list.append('NA')
        out_list.append(row_list)
    return out_list

def main():
    parser = argparse.ArgumentParser()
    req = parser.add_argument_group('required arguments')
    opt = parser.add_argument_group('optional arguments')

    req.add_argument('-i',
        help = 'input mis-aligned csv file',
        metavar = '',
        required=True)
    opt.add_argument('-o',
        default = None,
        help='optional output file name',
        metavar='')
    args = parser.parse_args()
    pheno_file = args.i
    
    # TODO add arguement to allow different delims
    pheno_list = pheno_to_list(pheno_file)
    aligned_pheno = proper_aligner(pheno_list)
    if args.o is None:
        out_file_handle = pheno_file.split('.')[0] + '_fixed_alignment.csv'
    else:
        out_file_handle = args.o

    with open(out_file_handle, 'w+') as open_out_file:
        open_csv = csv.writer(open_out_file)
        open_csv.writerows(aligned_pheno)


if __name__ == '__main__':
    main()
