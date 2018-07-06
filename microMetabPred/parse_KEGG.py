import asyncio
import aiohttp

# Parsers
def parse_ko(ko_raw_record):
    ko_dict = dict()
    past_entry = None
    for line in ko_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name != '':
            if current_entry_name == 'ENTRY':
                ko_dict[current_entry_name] = current_entry_data.split()[0]
            elif current_entry_name == 'NAME':
                ko_dict[current_entry_name] = current_entry_data.split(', ')
            elif current_entry_name == 'DEFINITION':
                ko_dict[current_entry_name] = current_entry_data
            elif current_entry_name in ('PATHWAY', 'MODULE', 'DISEASE'):
                split_current_entry_data = current_entry_data.split()
                current_entry_pathway_id = split_current_entry_data[0]
                current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
                if current_entry_name not in ko_dict:
                    ko_dict[current_entry_name] = list()
                ko_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
            elif current_entry_name == 'CLASS':
                if 'CLASS' in ko_dict:
                    ko_dict['CLASS'].append(current_entry_data)
                else:
                    ko_dict['CLASS'] = [current_entry_data]
            elif current_entry_name == 'BRITE':
                pass
            elif current_entry_name == 'DBLINKS' or current_entry_name == 'GENES':
                split_current_entry_data = current_entry_data.split(': ')
                if current_entry_name not in ko_dict:
                    ko_dict[current_entry_name] = dict()
                ko_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
            elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL', 'SEQUENCE'):
                pass
            else:
                raise ValueError('What is %s in %s?' % (current_entry_name, ko_dict['ENTRY']))
        past_entry = current_entry_name
    return ko_dict


def parse_rn(rn_raw_record):
    rn_dict = dict()
    past_entry = None
    for line in rn_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            rn_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name in ('NAME', 'DEFINITION', 'REMARK','COMMENT', 'ENZYME'):
            rn_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'RPAIR':
            rn_dict[current_entry_name] = current_entry_data.split()
        elif current_entry_name == 'DEFINITION' or current_entry_name == 'EQUATION':
            equation_split = current_entry_data.split(' <=> ')
            if len(equation_split) != 2:
                raise ValueError("Equation does not have two parts: %s" % current_entry_data)
            rn_dict[current_entry_name] = [(equation_split[0].strip().split(' + ')),
                                           (equation_split[1].strip().split(' + '))]
        elif current_entry_name in ('RCLASS', 'PATHWAY', 'ORTHOLOGY', 'MODULE'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in rn_dict:
                rn_dict[current_entry_name] = list()
            rn_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in rn_dict:
                rn_dict[current_entry_name] = dict()
                rn_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        else:
            raise ValueError('What is %s in %s?' % (current_entry_name, rn_dict['ENTRY']))
        past_entry = current_entry_name
    return rn_dict


def parse_co(co_raw_record):
    co_dict = dict()
    past_entry = None
    for line in co_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            co_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name == 'NAME':
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = current_entry_data
            else:
                co_dict[current_entry_name] += ' %s' % current_entry_data
        elif current_entry_name in ('FORMULA', 'EXACT_MASS', 'MOL_WEIGHT', 'REMARK', 'COMMENT'):
            co_dict[current_entry_name] = current_entry_data
        elif current_entry_name in ('REACTION', 'ENZYME', 'SEQUENCE'):
            if current_entry_name in co_dict:
                co_dict[current_entry_name] += current_entry_data.split()
            else:
                co_dict[current_entry_name] = current_entry_data.split()
        elif current_entry_name in ('PATHWAY', 'MODULE'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                co_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        # Structural information we are currently ignoring
        elif current_entry_name in ('BRITE', 'ATOM', 'BOND', 'BRACKET', 'ORIGINAL', 'REPEAT'):
            pass
        # Protein information we are currently ignoring
        elif current_entry_name in ('SEQUENCE', 'GENE', 'ORGANISM'):
            pass
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = dict()
                co_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        # Reference information we are currently ignoring
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        else:
            raise ValueError('What is %s in %s?' % (current_entry_name, co_dict['ENTRY']))
        past_entry = current_entry_name
    return co_dict


def parse_pathway(pathway_raw_record):
    pathway_dict = dict()
    past_entry = None
    for line in pathway_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            pathway_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name in ('NAME', 'DESCRIPTION', 'KO_PATHWAY'):
            pathway_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'CLASS':
            pathway_dict[current_entry_name] = [(i[:5], i[6:]) for i in current_entry_data.split('; ')]
        elif current_entry_name in ('PATHWAY_MAP', 'MODULE', 'DISEASE', 'DRUG', 'ORTHOLOGY', 'COMPOUND', 'REL_PATHWAY',
                                    'REACTION', 'ENZYME'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in pathway_dict:
                pathway_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                pathway_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        # Protein information we are currently ignoring
        elif current_entry_name in ('GENE', 'ORGANISM'):
            pass
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in pathway_dict:
                pathway_dict[current_entry_name] = dict()
                pathway_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        elif current_entry_name != current_entry_name.upper():
            pass
        else:
            raise ValueError('What is %s in %s?' % (line, pathway_dict['ENTRY']))
        past_entry = current_entry_name
    return pathway_dict


def parse_organism(gene_raw_record):
    gene_dict = dict()
    past_entry = None
    for line in gene_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            gene_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name == 'NAME':
            gene_dict[current_entry_name] = current_entry_data.split(', ')
        elif current_entry_name in ('DEFINITION', 'POSITION'):
            gene_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'ORTHOLOGY':
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            gene_dict[current_entry_name] = (current_entry_pathway_id, current_entry_pathway_name)
        elif current_entry_name in ('PATHWAY', 'DISEASE'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in gene_dict:
                gene_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                gene_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        elif current_entry_name == 'CLASS':
            if current_entry_name in gene_dict:
                gene_dict[current_entry_name].append(current_entry_data)
            else:
                gene_dict[current_entry_name] = [current_entry_data]
        elif current_entry_name in ('DRUG_TARGET', 'MOTIF', 'DBLINKS', 'STRUCTURE'):
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in gene_dict:
                gene_dict[current_entry_name] = dict()
                gene_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        # Sequence information I am currently ignoring
        elif current_entry_name in ('AASEQ', 'NTSEQ'):
            pass
        elif current_entry_name != current_entry_name.upper():
            pass
        else:
            raise ValueError('What is %s in %s?' % (line, gene_dict['ENTRY']))
        past_entry = current_entry_name
    return gene_dict


# Getting KEGG records from a flat file
def get_from_kegg_flat_file(file_loc, list_of_ids=None, parser=parse_ko):
    record_list = list()
    for entry in open(file_loc).read().split('///')[:-1]:
        record = parser(entry)
        if list_of_ids is not None:
            if record['ENTRY'] in list_of_ids:
                record_list.append(record)
        else:
            record_list.append(record)
    return record_list


# Getting KEGG records from the KEGG API
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


async def download_coroutine(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            raise ValueError('Bad connection: %s' % url)


async def kegg_download_manager(loop, list_of_ids):
    urls = ['http://rest.kegg.jp/get/%s' % '+'.join(chunk) for chunk in chunks(list(list_of_ids), 10)]

    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [download_coroutine(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return [raw_record for raw_records in results for raw_record in raw_records.split('///')[:-1]]


def get_from_kegg_api(list_of_ids, parser):
    loop = asyncio.get_event_loop()
    return [parser(raw_record) for raw_record in loop.run_until_complete(kegg_download_manager(loop, list_of_ids))]


# Getting a dictionary of kegg records from either the KEGG API or file files
def get_kegg_record_dict(list_of_ids, parser, records_file_loc=None, verbose=False):
    if records_file_loc is None:
        records = get_from_kegg_api(list_of_ids, parser)
    else:
        records = get_from_kegg_flat_file(records_file_loc, list_of_ids, parser)
    if verbose:
        print("%s records acquired" % len(records))
    return {record['ENTRY']: record for record in records}
