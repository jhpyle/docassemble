import pandas
from docassemble.base.util import path_and_mimetype

__all__ = ['get_fruit_names', 'fruit_info']

fruit_info_by_name = dict()
fruit_names = list()

def read_data(filename):
    the_xlsx_file, mimetype = path_and_mimetype(filename)
    df = pandas.read_excel(the_xlsx_file)
    for indexno in df.index:
        if not df['Name'][indexno]:
            continue
        fruit_names.append(df['Name'][indexno])
        fruit_info_by_name[df['Name'][indexno]] = {"color": df['Color'][indexno], "seeds": df['Seeds'][indexno]}

def get_fruit_names():
    return fruit_names

def fruit_info(fruit):
    if fruit not in fruit_info_by_name:
        raise Exception("Reference to invalid fruit " + fruit)
    return fruit_info_by_name[fruit]
        
read_data('docassemble.demo:data/sources/fruit_data.xlsx')
