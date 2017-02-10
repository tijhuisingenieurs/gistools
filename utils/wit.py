from utils.geometry import TLine, TMultiLineString

        
def create_leggerpunten(line,TI_waterbr, TI_talulbr, TI_bodembr):
    """ create point of profile based on theoretical profile of waterway
    line: line representation of waterway
    TI_waterbr: widht of profile in waterway
    TI_talulbr: width of left slope from waterline to bottom
    TI_bodembr: width of waterway flat bottom
    
    returns collection with:
        point at start of profile (also known as 22-left point)
        point at left inflection
        point at right inflection
        point at end of profile (also known as 22-right point)
    """
        

    point = line.get_point_at_percentage(0.5)
    profiel = TLine(line.get_haakselijn_point(point,TI_waterbr))
        
    nulpunt = list(profiel.coords)[0]    
    eindpunt = list(profiel.coords)[2]
    

    knikpunt_l = list(profiel.get_point_at_distance(TI_talulbr).coords)[0]
    knikpunt_r = list(profiel.get_point_at_distance((TI_talulbr + TI_bodembr)).coords)[0]
    
    profiel_dict = {'22L':nulpunt,'22L_peil': 0.00,
                    'knik_l': knikpunt_l, 'knik_l_dpt': 0.00,
                    'knik_r': knikpunt_r, 'knik_r_dpt': 0.00,
                    '22R':eindpunt, '22R_peil': 0.00}
    
    return profiel_dict
    
def update_leggerpunten_diepten(profiel_dict,leggerdiepten):    
    """ append correct depths to leggerpunten in profiel_dict
    
    profiel_dict: dictionary with 4 points of theoretical profile
    leggerdiepten: list of 4 depths to append
    
    return: profiel_dict with depts
    """
    
    profiel_dict['22L_peil'] = leggerdiepten[0]
    profiel_dict['knik_l_dpt'] = leggerdiepten[1]
    profiel_dict['knik_r_dpt'] = leggerdiepten[2]
    profiel_dict['22R_peil'] = leggerdiepten[3]
    
    return profiel_dict
    

