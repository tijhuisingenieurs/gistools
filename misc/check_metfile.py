# Script dat van een metfile leest en dan checkt of de profielinformatie en de metingen genoeg elementen hebben.
# Dit geeft nu namelijk een fout bij het inlezen van de data voor Wetterskip
# Geeft een lijst terug met daarin de profielnamen waarin een fout zit

import os
import csv
path_input = 'K:\Tekeningen Amersfoort\\2018\TI18275 Wetterskip WIT missende profielen\Tekening\Bewerkingen\Uitzoeken_profielen_watergangen_versie_2\Voorbereiding_9okt\\van_mails_everts\\naverwerking\Inlezen_WIT'
path_metfile = os.path.join(path_input,'cluster 15 versie 2.met')
#path_metfile = os.path.join(path_input,'cluster 23 versie 3-aangepast.met')

# List om alle informatie op te slaan
info_list = []

with open (path_metfile, 'r') as metfile:
    print 'Metfile geopend: ', metfile

    # Maakt de info als 1 lange text, handig om in te zoeken
    met = metfile.read().replace('\n', '').replace('\r', '')

    # Split de data op profielniveau
    profielen = met.split('<PROFIEL>')

    # Ga elk profiel af
    for each in profielen[1:]:
        profiel_elementen_totaal = each.split(',')
        profielnaam = profiel_elementen_totaal[0]
        print 'Profiel: ', profielnaam

        # Check of elk profiel ook een afsluitcommand heeft
        if profiel_elementen_totaal[-1] != '</METING></PROFIEL>':
            if profielnaam not in info_list:
                info_list.append(profielnaam)
                print 'Afsluiting missend: </PROFIEL>'

        # Check of er fouten zitten in de profielinfo, normaal gezien zou het 10e element de eerste meting bevatten,
        # zo niet dan zit er hoogstwaarschijnlijk een fout in de info
        if profiel_elementen_totaal[10].find('<METING>') < 0:
            if profielnaam not in info_list:
                info_list.append(profielnaam)
                print 'Fout in profielinfo'

        # Split het profiel op metingniveau
        metingen = each[1:].split('<METING>')
        # Check of er fouten zitten in de metingen, ga elk meetpunt af
        for meetpunt in metingen[1:]:
            meetpunt_elementen = meetpunt.split(',')

            # Check of elk meting ook een afsluitcommand heeft
            if meetpunt_elementen[-1]!= '</METING>' and meetpunt_elementen[-1]!= '</METING></PROFIEL>':
                if profielnaam not in info_list:
                    info_list.append(profielnaam)
                    print  'Afsluiting missend: </METING>'

            # Check op het aantal elementen in de meting, normaliter zijn dat er 6
            aantal_elementen =  len(meetpunt_elementen)-1 # de </meting> is ook een element, vandaar -1
            if aantal_elementen != 6:
                if profielnaam not in info_list:
                    info_list.append(profielnaam)
                    print 'Fout in meting'
metfile.close()

print 'Deze profielen zijn incorrect:'
print info_list
print 'Aantal incorrecte profielen: ',len(info_list)
