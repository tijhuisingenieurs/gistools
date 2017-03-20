from gistools.utils.geometry import TLine
from shapely.geometry import Point 


def vul_leggerwaarden(legger_col):
    """ fill ti-fields with correct source data and calculate
    derived values for creation of profiles
    
    receives legger_col with values for waterpeil, bodembreedte, 
    bodemhoogte, waterdiepte, breedte_wa, talud_l, talud_r
                      
    returns dictonary ti_velden with assigned values
    """
    
    # Vullen ti_velden dictionary met bronwaarden
    ti_waterp = legger_col['waterpeil']
    ti_diepte = legger_col['waterdiepte']
    ti_waterbr = legger_col['breedte_wa']
    ti_bodemh = legger_col['bodemhoogte']
    ti_bodembr = legger_col['bodembreedte']

    # berekenen van ontbrekende bronwaarden
    if ti_diepte == 0 or ti_diepte is None:
        # bodembreedte legger van toepassing
        ti_diepte = ti_waterp - ti_bodemh
    
    if ti_bodemh == 0 or ti_bodemh is None:
        # waterbreedte legger van toepassing
        ti_bodemh = ti_waterp - ti_diepte
        
    ti_talulbr = legger_col['talud_l'] * ti_diepte
    ti_talurbr = legger_col['talud_r'] * ti_diepte
    
    if ti_waterbr == 0 or ti_waterbr is None:
        # bodembreedte legger van toepassing
        ti_waterbr = ti_bodembr + ti_talulbr + ti_talurbr    
   
    if ti_bodembr == 0 or ti_bodembr is None:
        # waterbreedte legger van toepassing
        ti_bodembr = ti_waterbr - ti_talulbr - ti_talurbr
    
    ti_knkbodr = ti_talulbr + ti_bodembr
    
    # Vullen dictionary ti_velden
    ti_velden = {'ti_waterp': ti_waterp,
                 'ti_diepte': ti_diepte,
                 'ti_waterbr': ti_waterbr,
                 'ti_bodemh': ti_bodemh,
                 'ti_bodembr': ti_bodembr,
                 'ti_talulbr': ti_talulbr,
                 'ti_talurbr': ti_talurbr,
                 'ti_knkbodr': ti_knkbodr}   

    return ti_velden


def create_leggerpunten(line, line_id, name, ti_waterbr, ti_talulbr, ti_knkbodr):
    """ create point of profile based on theoretical profile of waterway
    line: line representation of waterway
    ti_waterbr: widht of profile in waterway
    ti_talulbr: width of left slope from waterline to bottom
    ti_knkbodr: width of waterway flat bottom plus left slope
    
    returns collection with:
        point at start of profile (also known as 22-left point)
        point at left inflection
        point at right inflection
        point at end of profile (also known as 22-right point)
    """
      
    point = line.get_point_at_percentage(0.5)
    profiel = TLine(line.get_haakselijn_point(Point(point), ti_waterbr))
        
    nulpunt = list(profiel.coords)[0]    
    eindpunt = list(profiel.coords)[2]

    knikpunt_l = profiel.get_point_at_distance(ti_talulbr)
    knikpunt_r = profiel.get_point_at_distance(ti_knkbodr)
    
    profiel_dict = {'line_id': line_id, 'name': name,
                    'L22': nulpunt, 'L22_peil': 0.00,
                    'knik_l': knikpunt_l, 'knik_l_dpt': 0.00,
                    'knik_r': knikpunt_r, 'knik_r_dpt': 0.00,
                    'R22': eindpunt, 'R22_peil': 0.00,
                    'ti_talulbr': ti_talulbr,
                    'ti_knkbodr': ti_knkbodr,
                    'ti_waterbr': ti_waterbr}
    
    return profiel_dict


def update_leggerpunten_diepten(profiel_dict, ti_velden_col):    
    """ append correct depths to leggerpunten in profiel_dict
    
    profiel_dict: dictionary with 4 points of theoretical profile
    leggerdiepten: list of 4 depths to append
    
    return: profiel_dict with depts
    """

    profiel_dict['L22_peil'] = ti_velden_col['ti_waterp']
    profiel_dict['knik_l_dpt'] = ti_velden_col['ti_bodemh']
    profiel_dict['knik_r_dpt'] = ti_velden_col['ti_bodemh']
    profiel_dict['R22_peil'] = ti_velden_col['ti_waterp']
    
    return profiel_dict
