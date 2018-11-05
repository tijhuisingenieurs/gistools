import os
import csv
import pandas as pd

# ------------ Part1: Check the metfile
def check_metfile(input_file, output_file):
    ''' Functie die een metfile leest en dan checkt of de profielinformatie en de metingen genoeg elementen hebben. En
    allemaal een afsluiting. Geeft een excelbestand terug met daarin de profielnamen waarin een fout zit.
    Daarbij geeft de tool in een eigen tabblad het overzicht welke codes er in het profiel voorkomen. Deze
    informatie kan gebruikt worden om via draaitabel te checken of de codes kloppen.
    LET OP: deze tool kan de fout in de <PROFIEL> niet vinden
    input_file (str): path van metfile die gecontroleerd moet worden
    output_file (str): path van excelfile met fout opmerkingen
    return: -'''

    # dict om alle informatie op te slaan voor output excel
    headers = ['Profielnaam', 'Missende afsluiting profiel', 'Fout in profielinformatie', 'Fout in afsluiting meting',
               'Fout in metinginformatie']
    resultaten_dict = dict((header, []) for header in headers)

    # Maak een list om de codes van alle profielen op te slaan
    codes_list = []

    # Opening metfile en data inlezen
    with open (input_file, 'r') as metfile:
        # Maakt de info als 1 lange text, handig om in te zoeken
        met = metfile.read().replace('\n', '').replace('\r', '')

        # Split de data op profielniveau
        profielen = met.split('<PROFIEL>')

        # Ga elk profiel af
        for profiel in profielen[1:]:
            profiel_elementen = profiel.split(',')
            profielnaam = profiel_elementen[0]

            # Checkparameter of er een fout is, dus het profiel naar de output moet worden geschreven
            fout_aanwezig = False

            # Maak list om de fouten van dit profiel op te slaan
            resultaten_list = ['-'] * len(headers)
            resultaten_list[0] = profielnaam

            # Check of elk profiel ook een afsluitcommand heeft
            if profiel_elementen[-1] != '</METING></PROFIEL>':
                resultaten_list[1] = 'ja'
                fout_aanwezig = True
                #print('Afsluiting missend: </PROFIEL>')

            # Check of er fouten zitten in de profielinfo, normaal gezien zou het 10e element de eerste meting bevatten,
            # zo niet dan zit er hoogstwaarschijnlijk een fout in de info
            if len(profiel_elementen) < 10:
                resultaten_list[2] = 'ja'
                fout_aanwezig = True
                #print('Fout in profielinfo')
            elif profiel_elementen[10].find('<METING>') < 0:
                resultaten_list[2] = 'ja'
                fout_aanwezig = True
                #print('Fout in profielinfo')

            # Split het profiel op metingniveau
            metingen = profiel[1:].split('<METING>')
            # Check of er fouten zitten in de metingen, ga elk meetpunt af
            for meetpunt in metingen[1:]:
                meetpunt_elementen = meetpunt.split(',')

                # Check of elk meting ook een afsluitcommand heeft
                if meetpunt_elementen[-1]!= '</METING>' and meetpunt_elementen[-1]!= '</METING></PROFIEL>':
                    resultaten_list[3] = 'ja'
                    fout_aanwezig = True
                    #print('Afsluiting missend: </METING>')

                # Check op het aantal elementen in de meting, normaliter zijn dat er 6
                aantal_elementen =  len(meetpunt_elementen)-1 # de </meting> is ook een element, vandaar -1
                if aantal_elementen != 6:
                    resultaten_list[4] = 'ja'
                    fout_aanwezig = True
                    #print('Fout in meting')

                # Check of de elementen wel de juiste waarde/format hebben
                for ind, waarde in enumerate(meetpunt_elementen[:-1]):
                    # Test of de eerste waardes hele getallen zijn en een juiste code aangeven
                    if ind == 0:
                        try:
                            waarde = int(waarde)
                            # Maak een lijst van de codes die dit profiel heeft
                            codes_list.append((profielnaam,waarde))
                        except:
                            resultaten_list[4] = 'ja'
                            fout_aanwezig = True
                            #print('fout:0')

                    if ind == 1:
                        try:
                            waarde = int(waarde)
                        except:
                            resultaten_list[4] = 'ja'
                            fout_aanwezig = True
                            #print('fout:1')

                    # Test of de laatste waardes kommagetallen zijn
                    if ind in (2,3,4,5):
                        try:
                            waarde = float(waarde)
                        except:
                            resultaten_list[4] = 'ja'
                            fout_aanwezig = True
                            #print('fout:2-5')

            # Als er inderdaad een fout gevonden is, wordt deze toegevoegd aan de resultaten, die straks naar
            # excel worden geschreven
            if fout_aanwezig:
                for ind, value in enumerate(resultaten_list):
                    resultaten_dict[headers[ind]].append(value)

    metfile.close()

    #print('Deze profielen zijn incorrect:')
    #print(resultaten_dict['Profielnaam'])
    #print('Aantal incorrecte profielen: ',len(resultaten_dict['Profielnaam']))
    #print(resultaten_dict)

    # ------------ Part 2: write resultaten to xslx file --------------------------------
    # Create dataframe van de tabel met fouten
    df = pd.DataFrame.from_dict(resultaten_dict)
    #Order the colunms
    df=df[headers]

    # Create dataframe van de profielcodes
    df_codes = pd.DataFrame(codes_list, columns = ['Profielnaam','code'])

    # create a excel writer
    writer = pd.ExcelWriter(output_file)

    # Convert the dataframe to an  Excel object.
    df.to_excel(writer, sheet_name='fouten_report')
    df_codes.to_excel(writer, sheet_name='overzicht_profielcodes')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
