import os
import csv
import pandas as pd

# ------------ Part1: Check the metfile
def check_metfile(input_file, output_file):
    ''' Functie die een metfile leest en dan checkt of de profielinformatie en de metingen genoeg elementen hebben. En
    allemaal een afsluiting. Geeft een excelbestand terug met daarin de profielnamen waarin een fout zit
    LET OP: deze tool kan de fout in de <PROFIEL> niet vinden'''

    # dict om alle informatie op te slaan voor output excel
    headers = ['Profielnaam', 'Missende afsluiting profiel', 'Fout in profielinformatie', 'Fout in afsluiting meting',
               'Fout in metinginformatie']
    resultaten_dict = dict((each, []) for each in headers)

    # Opening metfile en data inlezen
    with open (input_file, 'r') as metfile:
        #print 'Metfile geopend: ', metfile

        # Maakt de info als 1 lange text, handig om in te zoeken
        met = metfile.read().replace('\n', '').replace('\r', '')

        # Split de data op profielniveau
        profielen = met.split('<PROFIEL>')

        # Ga elk profiel af
        for each in profielen[1:]:
            profiel_elementen_totaal = each.split(',')
            profielnaam = profiel_elementen_totaal[0]
            #print 'Profiel: ', profielnaam

            # Checkparameter of er een fout is, dus het profiel naar de output moet worden geschreven
            fout_aanwezig = False

            # Maak list om de fouten van dit profiel op te slaan
            resultaten_list = ['-'] * len(headers)
            resultaten_list[0] = profielnaam

            # Check of elk profiel ook een afsluitcommand heeft
            if profiel_elementen_totaal[-1] != '</METING></PROFIEL>':
                resultaten_list[1] = 'ja'
                fout_aanwezig = True
                #print 'Afsluiting missend: </PROFIEL>'

            # Check of er fouten zitten in de profielinfo, normaal gezien zou het 10e element de eerste meting bevatten,
            # zo niet dan zit er hoogstwaarschijnlijk een fout in de info
            if len(profiel_elementen_totaal) < 10:
                resultaten_list[2] = 'ja'
                fout_aanwezig = True
                #print 'Fout in profielinfo'
            elif profiel_elementen_totaal[10].find('<METING>') < 0:
                resultaten_list[2] = 'ja'
                fout_aanwezig = True
                #print 'Fout in profielinfo'

            # Split het profiel op metingniveau
            metingen = each[1:].split('<METING>')
            # Check of er fouten zitten in de metingen, ga elk meetpunt af
            for meetpunt in metingen[1:]:
                meetpunt_elementen = meetpunt.split(',')

                # Check of elk meting ook een afsluitcommand heeft
                if meetpunt_elementen[-1]!= '</METING>' and meetpunt_elementen[-1]!= '</METING></PROFIEL>':
                    resultaten_list[3] = 'ja'
                    fout_aanwezig = True
                    #print  'Afsluiting missend: </METING>'

                # Check op het aantal elementen in de meting, normaliter zijn dat er 6
                aantal_elementen =  len(meetpunt_elementen)-1 # de </meting> is ook een element, vandaar -1
                if aantal_elementen != 6:
                    resultaten_list[4] = 'ja'
                    fout_aanwezig = True
                    #print 'Fout in meting'

                # Check of de elementen wel de juiste waarde/format hebben
                for ind, e in enumerate(meetpunt_elementen[:-1]):
                    # Test of de eerste waardes hele getallen zijn en een juiste code aangeven

                    if ind == 0 or ind == 1:
                        try:
                            e = int(e)
                        except:
                            resultaten_list[4] = 'ja'
                            fout_aanwezig = True
                            #print 'fout:01'
                        # if ind == 0 and e not in [1,2,5,6,7,22,99]:
                        #     resultaten_list[4] = 'ja'
                        #     fout_aanwezig = True
                        #     #print 'fout:00'
                        # if ind == 1 and e not in [92,999]:
                        #     resultaten_list[4] = 'ja'
                        #     fout_aanwezig = True
                        #     #print 'fout:11'

                    # Test of de laatste waardes kommagetallen zijn
                    if ind in (2,3,4,5):
                        try:
                            e = float(e)
                        except:
                            resultaten_list[4] = 'ja'
                            fout_aanwezig = True
                            #print 'fout:2-5'

            # Als er inderdaad een fout gevonden is, wordt deze toegevoegd aan de resultaten, die straks naar
            # excel worden geschreven
            if fout_aanwezig:
                for ind, value in enumerate(resultaten_list):
                    resultaten_dict[headers[ind]].append(value)

    metfile.close()

    #print 'Deze profielen zijn incorrect:'
    #print resultaten_dict['Profielnaam']
    #print 'Aantal incorrecte profielen: ',len(resultaten_dict['Profielnaam'])
    #print resultaten_dict

    # ------------ Part 2: write resultaten to xslx file --------------------------------
    # Create dataframe
    df = pd.DataFrame.from_dict(resultaten_dict)
    #Order the colunms
    df=df[headers]

    # create a excel writer
    writer = pd.ExcelWriter(output_file)
    # Convert the dataframe to an  Excel object.
    df.to_excel(writer, sheet_name='Sheet1')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()