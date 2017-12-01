# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import numpy as np

""""
Created on Thu Jun  1 12:44:58 2017

@author: madeleine

Issue #160

Author: Madeleine
Usage:python3 populate_casgenes.py

Populates CasProtein and OrganismCasPair tables
"""

# table of cas proteins from Makarova et al 2015
casprofiles = "data/crispr_type.csv"

with open(casprofiles, 'r', encoding='utf8') as f:
    profiles = np.loadtxt(f, dtype='S', delimiter='\t')


def populate_cas():
    print("Populating CasProtein table...")
    for row in profiles:
        profile_id = row[0].decode('utf8')
        function = row[2].decode('utf8')
        gene = row[3].decode('utf8')
        group = row[4].decode('utf8')
        type_spec = row[5].decode('utf8')
        casprotein, created = CasProtein.objects.get_or_create(
            profileID=profile_id,
            function=function,
            gene=gene,
            group=group,
            type_specificity=type_spec
        )
    print("Done.")
    return


def populate_organismcaspair():
    print("Populating OrganismCasPair table...")
    # these are files split by organism accession
    for fn in os.listdir("gbfiles/hmmeroutput"):
        # HMMER output results
        data = np.loadtxt("gbfiles/hmmeroutput/%s" % fn, dtype='S')
        # organism accession number
        accid = fn.rsplit('.')[0]

        # retrieve organism from database
        organismset = Organism.objects.filter(accession=accid)

        if not organismset.exists():
            print('Organism with accid %s not found in db' % accid)
            continue
        # this is the organism FK for the field organism
        organism = organismset[0]

        querylist = []
        # iterate over HMMER matches to cas protein profiles
        for row in data:
            if not data[0].shape:
                row = data
            query = row[2].decode('utf8')  # cds start and end
            evalue = row[4].decode('utf8')
            target_match = row[0].decode('utf8')
            # retrieve cas protein entry from database
            casproteinset = CasProtein.objects.filter(profileID=target_match)

            if not casproteinset.exists():
                print('Cas protein with profileID {} not found in db'.format(
                    target_match))
                continue
            # this is the cas protein FK for the field casprotein
            casprotein = casproteinset[0]

            if query not in querylist:
                # we only keep 1 match if there are multiple
                querylist.append(query)

                # check if sequence is complemented - if yes, start
                # will be > end
                if query[:10] == 'complement':
                    query = query[11:-1]
                try:
                    start, dot, end = query.rsplit('.')
                    start = start.strip('<>')
                    end = end.strip('<>')
                    start = int(start)
                    end = int(end)
                except Exception as e:
                    print('Error accession {} with query {} with profile {} '
                          'for error {}'.format(organism.accession,
                                                query,
                                                target_match,
                                                e))
                    continue
                evalue = float(evalue)
                osrpair, created = OrganismCasProtein.objects.get_or_create(
                    organism=organism,
                    casprotein=casprotein,
                    genomic_start=start,
                    genomic_end=end,
                    evalue=evalue
                )
    print("Done.")
    return


if __name__ == '__main__':
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phageAPI.settings")
    django.setup()
    from restapi.models import Organism, CasProtein, OrganismCasProtein

    populate_cas()
    populate_organismcaspair()
