import math
import pandas as pd
import numpy as np

class IND_POPULATION:
    OBJECT_NUMBER = 0

    def __init__(self, data='data/3. CLEAN\A-02 Decadal variation in population 1901-2011.csv'):
        self.data = pd.read_csv(data)
        self.data_optimization()

        IND_POPULATION.OBJECT_NUMBER += 1
        print("IND_POPULATION object created", IND_POPULATION.OBJECT_NUMBER)

    def data_optimization(self):
        # Handling missing values
        self.data_nan() # There is no missing values in the data is already cleaned

        # converting data types
        self.data['State Code'] = self.data['State Code'].astype('int8')
        self.data['State Name'] = self.data['State Name'].astype('category')
        self.data['District Code'] = self.data['District Code'].astype('int16')
        self.data['District Name'] = self.data['District Name'].astype('category')
        # self.data['Census Year'] = pd.to_datetime(self.data['Census Year'], format='%Y')
        self.data['Persons'] = self.data['Persons'].astype('int32')
        self.data['Males'] = self.data['Males'].astype('int32')
        self.data['Females'] = self.data['Females'].astype('int32')
    
    def data_nan(self):
        self.data['State Name'] = self.data['State Name'].fillna('Unknown')
        self.data['District Name'] = self.data['District Name'].fillna('Unknown')
        
        # droping rows with missing values
        self.data = self.data.dropna()
        # droping duplicate rows
        self.data = self.data.drop_duplicates()
        # droping columns with all values as NaN
        self.data = self.data.dropna(axis=1, how='all')

    # utility functions
    def get_population_data(self):
        return self.data

    def get_state(self, state_code=None):
        if state_code is None:
            return self.data[['State Code', 'State Name']].drop_duplicates().reset_index(drop=True).set_index('State Code').to_dict()
        else:
            return self.data[['State Code', 'State Name']][self.data['State Code'].isin(state_code)].drop_duplicates().reset_index(drop=True).set_index('State Code').to_dict()

    def get_district(self, state_code=None, district_code=None):
        if state_code is None and district_code is None:
            return self.data[['District Code', 'District Name']].drop_duplicates().reset_index(drop=True).set_index('District Code').to_dict()
        else:
            return self.data[['District Code', 'District Name']][(self.data['State Code'].isin(state_code) if state_code else True) & (self.data['District Code'].isin(district_code) if district_code else True)].drop_duplicates().reset_index(drop=True).set_index('District Code').to_dict()

    
    def get_population(self, state_code=None, district_code=None, census_year=None):
        # District Code is unique and never repeated in other states
        if state_code is None and district_code is None and census_year is None:
            return self.data
        else:
            return self.data[(self.data['State Code'].isin(state_code) if state_code else True) & (self.data['District Code'].isin(district_code) if district_code else True) & (self.data['Census Year'].isin(census_year) if census_year else True)]

if __name__ == '__main__':
    obj = IND_POPULATION()
    print(obj.data.head())
    print(obj.data.info())
    print(IND_POPULATION.OBJECT_NUMBER)
    # print(obj.get_population([1], None, ['1921-01-01']))
    # print(obj.get_state([]))
    print(obj.get_district(None, None))
