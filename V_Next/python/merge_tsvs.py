import os
import shutil
import logging
import argparse
import pickle
import traceback

import pybedtools
import numpy as np


def merge_tsvs(input_tsvs, out,
               candidates_per_tsv, max_num_tsvs, overwrite_merged_tsvs,
               keep_none_types, max_dp=1000000):
    logger = logging.getLogger(merge_tsvs.__name__)
    logger.info("----------------Merging Candidate tsvs-------------------")
    if not os.path.exists(out):
        os.mkdir(out)
    out_mreged_folder = os.path.join(out, "merged_tsvs")
    if os.path.exists(out_mreged_folder):
        if overwrite_merged_tsvs:
            shutil.rmtree(out_mreged_folder)
        else:
            i = 1
            while os.path.exists(out_mreged_folder):
                out_mreged_folder = os.path.join(
                    out, "merged_tsvs_{}".format(i))
                i += 1
    os.mkdir(out_mreged_folder)
    n_var_file = 0
    var_file = os.path.join(
        out_mreged_folder, "merged_var_{}.tsv".format(n_var_file))
    var_f = open(var_file, "w")
    var_idx = []
    n_none_file = 0
    if not keep_none_types:
        none_file = os.path.join(
            out_mreged_folder, "merged_none_{}.tsv".format(n_none_file))
        none_f = open(none_file, "w")
        none_idx = []
    merged_tsvs = []

    totla_L = 0
    for tsv in input_tsvs:
        totla_L += len(pickle.load(open(tsv + ".idx", "rb"))) - 1
    totla_L = max(0, totla_L)
    candidates_per_tsv = max(candidates_per_tsv, np.ceil(
        totla_L / float(max_num_tsvs)) + 1)

    for tsv in input_tsvs:
        logger.info("tsv:{}, merge_id: {}".format(tsv, len(merged_tsvs)))
        with open(tsv, "r") as i_f:
            for line in i_f:
                fields = line.strip().split()
                tag = fields[2]
                _, _, _, _, _, _, _, tumor_cov, normal_cov = tag.split(".")
                tumor_cov = int(tumor_cov)
                normal_cov = int(normal_cov)
                if tumor_cov > max_dp:
                    logger.info("Ignore {}".format(tag))
                    continue
                is_none_type = "NONE" in tag
                if not keep_none_types and is_none_type:
                    fields[0] = str(len(none_idx))
                    line = "\t".join(fields) + "\n"
                    none_idx.append(none_f.tell())
                    none_f.write(line)
                    if len(none_idx) >= candidates_per_tsv:
                        none_idx.append(none_f.tell())
                        pickle.dump(none_idx, open(none_file + ".idx", "wb"))
                        none_f.close()
                        logger.info(
                            "Done with merge_id: {}".format(len(merged_tsvs)))
                        merged_tsvs.append(none_file)
                        n_none_file += 1
                        none_file = os.path.join(
                            out_mreged_folder, "merged_none_{}.tsv".format(n_none_file))
                        none_f = open(none_file, "w")
                        none_idx = []
                else:
                    fields[0] = str(len(var_idx))
                    line = "\t".join(fields) + "\n"
                    var_idx.append(var_f.tell())
                    var_f.write(line)
                    if len(var_idx) >= candidates_per_tsv:
                        var_idx.append(var_f.tell())
                        pickle.dump(var_idx, open(var_file + ".idx", "wb"))
                        var_f.close()
                        logger.info(
                            "Done with merge_id: {}".format(len(merged_tsvs)))
                        merged_tsvs.append(var_file)
                        n_var_file += 1
                        var_file = os.path.join(
                            out_mreged_folder, "merged_var_{}.tsv".format(n_var_file))
                        var_f = open(var_file, "w")
                        var_idx = []
    if not var_f.closed:
        var_idx.append(var_f.tell())
        pickle.dump(var_idx, open(var_file + ".idx", "wb"))
        var_f.close()
        logger.info("Done with merge_id: {}".format(len(merged_tsvs)))
        merged_tsvs.append(var_file)
    if not keep_none_types and not none_f.closed:
        none_idx.append(none_f.tell())
        pickle.dump(none_idx, open(none_file + ".idx", "wb"))
        none_f.close()
        logger.info("Done with merge_id: {}".format(len(merged_tsvs)))
        merged_tsvs.append(none_file)

    logger.info("Merged input tsvs to: {}".format(merged_tsvs))
    return merged_tsvs

if __name__ == '__main__':

    FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Resolve ambigues variants')
    parser.add_argument('--input_tsvs', nargs="*",
                        help=' input candidate tsv files', required=True)
    parser.add_argument('--out', type=str,
                        help='output directory', required=True)
    parser.add_argument('--candidates_per_tsv', type=int,
                        help='Maximum number of candidates in each merged tsv file ',
                        default=10000000)
    parser.add_argument('--max_num_tsvs', type=int,
                        help='Maximum number of merged tsv files \
                        (higher priority than candidates_per_tsv)', default=10)
    parser.add_argument('--overwrite_merged_tsvs',
                        help='if OUT/merged_tsvs/ folder exists overwrite the merged tsvs',
                        action="store_true")
    parser.add_argument('--keep_none_types', action="store_true",
                        help='Do not split none somatic candidates to seperate files')
    args = parser.parse_args()
    logger.info(args)

    try:
        merged_tsvs = merge_tsvs(args.input_tsvs, args.out,
                                 args.candidates_per_tsv, args.max_num_tsvs,
                                 args.overwrite_merged_tsvs,
                                 args.keep_none_types)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Aborting!")
        logger.error(
            "merge_tsvs.py failure on arguments: {}".format(args))
        raise e
