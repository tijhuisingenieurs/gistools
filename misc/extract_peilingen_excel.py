import pandas as pd
import csv
import datetime

# Set filename
excel_file = "K:\Projecten\\2018\TI18070 Peilwerk Amersfoort\Veldwerk\\01_Nijkerk\Uitgelezen\GPS_Gegevens_Puntpeilingen.xlsx"
output_path = "K:\Projecten\\2018\TI18070 Peilwerk Amersfoort\Veldwerk\\01_Nijkerk\Uitgelezen\Puntpeilingen_Nijkerk.met"
reeks = "Nijkerk, puntpeilingen"

xl_input = pd.ExcelFile(excel_file)
df = xl_input.parse().sort_values('pp_name')

with open(output_path, 'wb') as csvfile:

    fieldnames = ['regel']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|',
                            quoting=csv.QUOTE_NONE,
                            quotechar='', escapechar='\\')

    current_profile = ''
    profile_end = '</PROFIEL>'

    # write version
    version = "<VERSIE>1.0</VERSIE>"
    writer.writerow({'regel': version})

    # write project data in REEKS
    project_tekst = "<REEKS>{0},</REEKS>".format(reeks)
    writer.writerow({'regel': project_tekst})

    for index, row in df.iterrows():
        profiel = str(row['pp_name'])
        datum = str(row['date'][5:])
        date = datetime.datetime.strptime(datum, "%m-%d-%Y")
        new_date = date.strftime("%Y%m%d")
        tekencode = 999

        x_coord = str(row['x'])
        y_coord = str(row['y'])

        up = row['bk'][2:]
        lo = row['ok'][2:]
        water_level = float(row['z_nap'])

        if up not in ["", " "]:
            upper_level = float(up)
            upper_level_nap = str(water_level - (upper_level / 100))
        else:
            upper_level_nap = ""

        if lo not in ["", " "]:
            lower_level = float(lo)
            lower_level_nap = str(water_level - (lower_level / 100))
        else:
            lower_level_nap = ""

        # wegschrijven profielregel
        profiel_tekst = "<PROFIEL>{0},{1},{2},0.00,NAP,ABS,2,XY,{3},{4},".format(
            profiel,
            profiel,
            new_date,
            x_coord,
            y_coord
        )

        writer.writerow({'regel': profiel_tekst})

        # wegschrijven meting regels 22 punt
        meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
            "22",
            tekencode,
            x_coord,
            y_coord,
            str(water_level),
            str(water_level)
        )
        writer.writerow({'regel': meting_tekst})

        # wegschrijven meting regels puntpeiling
        meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
            "99",
            tekencode,
            x_coord,
            y_coord,
            upper_level_nap,
            lower_level_nap
        )
        writer.writerow({'regel': meting_tekst})
        writer.writerow({'regel': profile_end})


























