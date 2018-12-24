import os
import os.path
import numpy as np
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import arcpy
from utils.addresulttodisplay import add_result_to_display
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.cm as cm
from gistools.utils.collection import MemCollection

def PCA_analysis(input_data):
    '''
    '''

    # Inlezen shapefile en omzetten naar dataframe
    rows_in = arcpy.SearchCursor(input_data)
    fields_in = arcpy.ListFields(input_data)
    properties_dict = {}
    for row in rows_in:
        properties = []
        kolom_namen = []
        for field in fields_in:
            if field.name.lower() != 'shape':
                if isinstance(field.name, unicode):
                    key = field.name.encode('utf-8')
                else:
                    key = field.name
                if isinstance(row.getValue(field.name), unicode):
                    value = row.getValue(field.name).encode('utf-8')
                else:
                    value = row.getValue(field.name)
                properties.append(value)
                kolom_namen.append(key)
        properties_dict[properties[2]] = properties[3:]

    # Verwijder de eerste kolomnamen, deze zijn niet interessant (FID, ID, en profnaam)
    del kolom_namen[:3]

    # Omzetten naar dataframe
    properties_df = pd.DataFrame.from_dict(properties_dict, orient='index')

    # Bekijken van de data: slibaanwas -> histogram
    slib_histogram = np.histogram(properties_df.ix[:,0], bins=10)
    # Visualisatie
    plt.figure()
    plt.hist(slib_histogram, bins='auto')
    plt.title('Histogram slibaanwas')

    plt.figure()
    plt.plot(properties_df.ix[:,0],properties_df.ix[:,1], '*')
    plt.xlabel('slibaanwas')
    plt.ylabel('breedte')

    plt.figure()
    plt.scatter(properties_df.ix[:,0],properties_df.ix[:,1],properties_df.ix[:,9])

    # Test colors iets
    x = properties_df.ix[:,0]
    ys = [i + x + (i * x) ** 2 for i in range(10)]
    plt.figure()
    colors = cm.rainbow(np.linspace(0, 1, len(x)))
    plt.scatter(properties_df.ix[:,0], properties_df.ix[:,1], color=colors[properties_df.ix[:,9]])
    # werkt nog niet zo als ik gedacht had



    # Standariseren van de gegevens
    # X_std = StandardScaler().fit_transform(properties_df)
    # mean_vec = np.mean(X_std, axis=0)
    # cov_mat = (X_std - mean_vec).T.dot((X_std - mean_vec)) / (X_std.shape[0] - 1)
    # print('Covariance matrix \n%s' % cov_mat)

    # Covarinace matrix: eigenvectors en eigenwaardes berekenen

    # Sorteren van de eigenvectors en eiegenwaardes


    # maak numpy array van de data
    properties_array = properties_df.values

    #
    k =2

# input_data = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\\berekenen_slibaanwas\proj_slibaanwas_all' \
#              '\Test_PCA_input.shp'
input_data = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\\berekenen_slibaanwas\proj_slibaanwas_all' \
             '\\result_alle_proj_data_0301.shp'
PCA_analysis(input_data)
plt.show()
