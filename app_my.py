import pandas as pd
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Paired
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, TableColumn, DataTable

zbior_danych = pd.read_csv('flight2_data_2016.csv', index_col=0)


def moja_tabela(initial_carriers):  

    by_carrier = pd.DataFrame(columns=['UNIQUE_CARRIER','count', 'mean','distance','air_time','air_speed (mph)','kolor'])

    for i, carrier_name in enumerate(initial_carriers):
        subset = zbior_danych[zbior_danych['UNIQUE_CARRIER'] == carrier_name]
        subset2 = pd.DataFrame(subset['UNIQUE_CARRIER'])
        subset2['count'] = subset['ARR_DELAY'].agg('count')
        mean_pomocnicza = subset['ARR_DELAY'].agg('mean')
        subset2['mean'] = round(mean_pomocnicza, 2)
        distance_pomocnicza = subset['DISTANCE'].agg('mean')
        subset2['distance'] = round(distance_pomocnicza, 2)
        air_time_pomocnicza = subset['AIR_TIME'].agg('mean')
        subset2['air_time'] = round(air_time_pomocnicza, 2)
        subset2 = subset2.drop_duplicates()
        predkosc_pomocnicza = subset['air_speed (mph)']
        subset2['air_speed (mph)'] = round(predkosc_pomocnicza,2)
        subset2['kolor'] = Paired[12][i]
        by_carrier = by_carrier.append(subset2)

    by_carrier = by_carrier.sort_values('UNIQUE_CARRIER')
    src = ColumnDataSource(by_carrier)

    return src



def moj_zbior_do_wykresu(lista_linii, zakres_start = -90, zakres_end = 120, szerokosc_slupka = 5):

    by_carrier = pd.DataFrame(columns=['loty','left', 'right','przedzial_min', 'nazwa','kolor'])

    zakres_extent = zakres_end - zakres_start

    for i, carrier_name in enumerate(lista_linii):

        subset = zbior_danych[zbior_danych['UNIQUE_CARRIER'] == carrier_name]
        arr_hist, krawedzie = np.histogram(subset['ARR_DELAY'], 
                                               bins = int(zakres_extent / szerokosc_slupka), 
                                               range = [zakres_start, zakres_end])
        arr_df = pd.DataFrame({'loty': arr_hist, 'left': krawedzie[:-1], 'right': krawedzie[1:]})
        arr_df['przedzial_min'] = ['%d do %d minut' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]
        arr_df['nazwa'] = carrier_name
        arr_df['kolor'] = Paired[12][i]
        by_carrier = by_carrier.append(arr_df)

    by_carrier = by_carrier.sort_values(['nazwa', 'left'])
    src2 = ColumnDataSource(by_carrier)

    return src2

def moj_zbior_do_wykresu2(lista_linii, zakres_start = 0, zakres_end = 180, szerokosc_slupka = 10):

    by_carrier = pd.DataFrame(columns=['loty','left', 'right','przedzial_min', 'nazwa','kolor'])

    zakres_extent = zakres_end - zakres_start

    for i, carrier_name in enumerate(lista_linii):

        subset = zbior_danych[zbior_danych['UNIQUE_CARRIER'] == carrier_name]
        arr_hist, krawedzie = np.histogram(subset['AIR_TIME'], 
                                               bins = int(zakres_extent / szerokosc_slupka), 
                                               range = [zakres_start, zakres_end])
        arr_df = pd.DataFrame({'loty': arr_hist, 'left': krawedzie[:-1], 'right': krawedzie[1:]})
        arr_df['przedzial_min'] = ['%d do %d minut' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]
        arr_df['nazwa'] = carrier_name
        arr_df['kolor'] = Paired[12][i]
        by_carrier = by_carrier.append(arr_df)

    by_carrier = by_carrier.sort_values(['nazwa', 'left'])
    src3 = ColumnDataSource(by_carrier)

    return src3

def update_src_scr2_src3(attr, old, new):
    aktualne_linie_lotnicze = [linie_lotnicze.labels[i] for i in linie_lotnicze.active]

    new_src = moja_tabela(aktualne_linie_lotnicze)
    
    new_src2 = moj_zbior_do_wykresu(aktualne_linie_lotnicze,
                                   zakres_start = zakres.value[0],
                                   zakres_end = zakres.value[1],
                                   szerokosc_slupka = szerokosc_slupka.value)
    new_src3 = moj_zbior_do_wykresu2(aktualne_linie_lotnicze,
                                   zakres_start = zakres2.value[0],
                                   zakres_end = zakres2.value[1],
                                   szerokosc_slupka = szerokosc_slupka2.value)

    src.data.update(new_src.data)
    src2.data.update(new_src2.data)
    src3.data.update(new_src3.data)
    
    
def styl_wykresu(czcionka):
    czcionka.title.align = 'center'
    czcionka.title.text_font_size = '15pt'
    czcionka.title.text_font = 'arial'
    czcionka.xaxis.major_label_text_font_size = '10pt'
    czcionka.yaxis.major_label_text_font_size = '10pt'
    czcionka.xaxis.axis_label_text_font_size = '12pt'
    czcionka.xaxis.axis_label_text_font_style = 'bold'
    czcionka.yaxis.axis_label_text_font_size = '12pt'
    czcionka.yaxis.axis_label_text_font_style = 'bold'

    return czcionka

def histogram(src2):
    wykres = figure(plot_width = 600, plot_height = 700, 
                title = 'Histogram opóźnień linii lotniczych US dla roku 2016',
                x_axis_label = 'Opóźnienie (min)', y_axis_label = 'Liczba lotów')

    wykres.quad(source = src2, bottom = 0, top = 'loty', left = 'left', right = 'right', 
           color = 'kolor', fill_alpha = 0.7, hover_fill_color = 'kolor', hover_fill_alpha = 0.4,
           legend = 'nazwa', line_color = 'black')

    hover = HoverTool(tooltips=[('Nazwa linii', '@nazwa'), ('Opóźnienie', '@przedzial_min'),('Liczba lotów', '@loty')],
                                mode='vline')
    wykres.add_tools(hover)
    wykres = styl_wykresu(wykres)

    return wykres

def histogram2(src3):
    wykres = figure(plot_width = 600, plot_height = 700, 
                title = 'Histogram czasu lotu linii lotniczych US dla roku 2016',
                x_axis_label = 'Czas lotu (min)', y_axis_label = 'Liczba lotów')

    wykres.quad(source = src3, bottom = 0, top = 'loty', left = 'left', right = 'right', 
           color = 'kolor', fill_alpha = 0.7, hover_fill_color = 'kolor', hover_fill_alpha = 0.4,
           legend = 'nazwa', line_color = 'black')

    hover = HoverTool(tooltips=[('Nazwa linii', '@nazwa'), ('Czas lotu', '@przedzial_min'),('Liczba lotów', '@loty')],
                                mode='vline')
    wykres.add_tools(hover)
    wykres = styl_wykresu(wykres)

    return wykres



nazwy_linii_lotniczych = list(set(zbior_danych['UNIQUE_CARRIER']))
nazwy_linii_lotniczych.sort()

airline_colors = Paired

linie_lotnicze= CheckboxGroup(labels=nazwy_linii_lotniczych, active = [0,1])
linie_lotnicze.on_change('active', update_src_scr2_src3)

szerokosc_slupka= Slider(start = 1, end = 30, step = 1, value = 5, title = 'Rozpiętość słupka (min)')
szerokosc_slupka.on_change('value', update_src_scr2_src3)

zakres= RangeSlider(start = -60, end = 180, value = (-60, 60), step = 5, title = 'Zakres opóźnień (min)')
zakres.on_change('value', update_src_scr2_src3)

szerokosc_slupka2= Slider(start = 1, end = 60, step =10, value = 20, title = 'Rozpiętość słupka (min)')
szerokosc_slupka2.on_change('value', update_src_scr2_src3)

zakres2= RangeSlider(start = 0, end = 400, value = (0,300), step = 10, title = 'Czas lotu (min)')
zakres2.on_change('value', update_src_scr2_src3)
    
aktualne_linie_lotnicze = [linie_lotnicze.labels[i] for i in linie_lotnicze.active]


src = moja_tabela(aktualne_linie_lotnicze)

src2 = moj_zbior_do_wykresu(aktualne_linie_lotnicze,
                           zakres_start = zakres.value[0],
                           zakres_end = zakres.value[1],
                           szerokosc_slupka = szerokosc_slupka.value)
src3 = moj_zbior_do_wykresu2(aktualne_linie_lotnicze,
                           zakres_start = zakres2.value[0],
                           zakres_end = zakres2.value[1],
                           szerokosc_slupka = szerokosc_slupka2.value)


columns = [TableColumn(field="UNIQUE_CARRIER", title="nazwa linii"),
           TableColumn(field="count", title="suma lotów"),
           TableColumn(field="mean", title="średnia opóźnien (min)"),
           TableColumn(field="distance", title="średni pokonywany dystans (mile)"),
           TableColumn(field="air_time", title="średni czas lotów (min)"),
           TableColumn(field="air_speed (mph)", title="średnia prędkość (mph)"),
           ]

datatable = DataTable(source=src, columns=columns, width=1100)
wykres = histogram(src2)
wykres2 = histogram2(src3)

p1=figure(plot_width = 350, plot_height = 350, 
                title = 'Opóźnienie względem dystansu',
                x_axis_label = 'Średnie opóźnienie (min)', y_axis_label = 'Średni dystans (mile)')
p1.circle("mean", "distance",size=20, color="kolor", source=src)

p2=figure(plot_width = 350, plot_height = 350, 
                title = 'Opóźnienie względem czasu lotu',
                x_axis_label = 'Średnie opóźnienie (min)', y_axis_label = 'Średni czas lotów (min)')
p2.circle("mean", "air_time",size=20, color="kolor", source=src)

p3=figure(plot_width = 350, plot_height = 350, 
                title = 'Opóźnienie względem prędkości lotu',
                x_axis_label = 'Średnie opóźnienie (min)', y_axis_label = 'Średnia prędkość lotu (mph)')
p3.circle("mean", "air_speed (mph)",size=20, color="kolor", source=src)

curdoc().add_root(row(column(szerokosc_slupka, zakres, wykres, szerokosc_slupka2, zakres2, wykres2), column(linie_lotnicze, p1,p2,p3, datatable)))
