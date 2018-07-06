import argparse

from microMetabPred.predict_metabolites import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--input', help="white space separated list of KEGG KO's from bacterial community",
                        required=True)
    parser.add_argument('-o', '--output_dir', help="directory to store output", required=True)
    parser.add_argument('--detected_compounds', help="list of compounds detected via metabolomics")
    parser.add_argument('--host_kos', help="white space separated list of KEGG KO's from host or other environment")
    parser.add_argument('--detected_only', help="only use detected metabolites in enrichment analysis",
                        action='store_true', default=False)

    parser.add_argument('--ko_file_loc', help='Location of ko file from KEGG FTP download')
    parser.add_argument('--rn_file_loc', help='Location of reaction file from KEGG FTP download')
    parser.add_argument('--co_file_loc', help='Location of compound file from KEGG FTP download')
    parser.add_argument('--pathway_file_loc', help='Location of pathway file from KEGG FTP download')

    args = parser.parse_args()
    kos_loc = args.input
    output_dir = args.output_dir
    detected_compounds = args.detected_compounds
    other_kos_loc = args.host_kos
    detected_only = args.detected_only

    ko_file_loc = args.ko_file_loc
    rn_file_loc = args.rn_file_loc
    co_file_loc = args.co_file_loc
    pathway_file_loc = args.pathway_file_loc

    if detected_only and detected_compounds is None:
        raise ValueError('Cannot have detected compounds only and not provide detected compounds')

    main(kos_loc, output_dir, detected_compounds, other_kos_loc, detected_only, ko_file_loc=ko_file_loc,
         rn_file_loc=rn_file_loc, co_file_loc=co_file_loc, pathway_file_loc=pathway_file_loc)