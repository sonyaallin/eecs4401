import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import rc
from scipy import stats


sns.set()


class Covid19Dataset():
    """
    A class for datasets with case and fatality numbers stratified by age
    group for different countries.
    """

    def __init__(self,
                 country,
                 date,
                 confirmed_cases,
                 fatalities,
                 source,
                 comments=None,
                 age_ranges=['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
                 ):
        self.country = country
        self.date = date
        self.confirmed_cases = np.array(confirmed_cases)
        self.fatalities = np.array(fatalities)
        self.source = source
        self.comments = comments
        self.age_ranges = age_ranges

        # compute quantities of interest
        self.cfr = self.fatalities / self.confirmed_cases
        self.total_cases = sum(self.confirmed_cases)
        self.total_fatalities = sum(self.fatalities)
        self.case_rates_by_age = self.confirmed_cases / self.total_cases
        self.total_cfr = sum(self.case_rates_by_age * self.cfr)


def autolabel(rects, ax, decimal_points=1, fontsize=10):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        text_offset = (0, 3) if height >= 0 else (-2, -13)
        ax.annotate(f"{height:.{decimal_points}f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=text_offset,
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=fontsize)


def bar_chart_by_age(datasets, type, show_numbers=True, size=None):
    n_data = len(datasets)
    w = 1 / n_data
    if size is not None:
        fig, ax = plt.subplots(figsize=size)

    else:
        fig, ax = plt.subplots()

    ax.set_xlabel('Age')
    ax.set_ylabel('%')
    i = 0
    for data in datasets:
        data_id = data.country + ', ' + data.date
        if type == 'cases_by_age':
            labels = datasets[0].age_ranges
            x = 1.25 * np.arange(len(labels))  # the label locations
            x_init = x - 0.5 + w / 2
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_title('Proportion of confirmed cases by age group')
            y = 100 * data.case_rates_by_age
            bar = ax.bar(x_init + i / n_data, y, w, label=data_id)

        elif type == 'cfr':
            labels = datasets[0].age_ranges + ['Total']
            x = 1.25 * np.arange(len(labels))  # the label locations
            x_init = x - 0.5 + w / 2
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_ylabel('%')
            ax.set_title('Case fatality rates (CFRs) by age group')
            y = np.append(100 * data.cfr, 100 * data.total_cfr)
            bar = ax.bar(x_init + i / n_data, y, w, label=data_id)

        else:
            raise NotImplementedError
            print("Plot type not supported. Please choose between 'cases_by_age' and 'cfr'.")

        i += 1
        if show_numbers:
            autolabel(bar, ax)

    ax.legend()
    fig.tight_layout()
    plt.show()
    return fig





if __name__ == "__main__":
    China_Feb17 = Covid19Dataset(
        country='China',
        date='17 February',
        confirmed_cases=[416, 549, 3619, 7600, 8571, 10008, 8583, 3918, 1408],
        fatalities=[0, 1, 7, 18, 38, 130, 309, 312, 208],
        source={
            'type': 'scientific publication',
            'title': 'Characteristics of and important lessons from the coronavirus\
                disease 2019 (COVID-19) outbreak in China: summary of a report of\
                72 314 cases from the Chinese Center for Disease Control and Prevention',
            'author': 'Wu, Zunyou and McGoogan, Jennifer M',
            'journal': 'Jama',
            'date': '24 February 2020',
            'url': 'https://jamanetwork.com/journals/jama/fullarticle/2762130'
        }
    )

    Italy_Mar9 = Covid19Dataset(
        country='Italy',
        date='9 March',
        confirmed_cases=[43, 85, 296, 470, 891, 1453, 1471, 1785, 1532],
        fatalities=[0, 0, 0, 0, 1, 3, 37, 114, 202],
        source={
            'type': 'official report',
            'date': '9 March 2020, 4pm',
            'author': 'Istituto Superiore di Sanità \
                (ISS, Italian National Institute of Health)',
            'url': 'https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-\sorveglianza-integrata-COVID-19_09-marzo-2020.pdf'
        }
    )

    data_Simpson = [China_Feb17, Italy_Mar9]
    fig = bar_chart_by_age(data_Simpson, 'cfr', show_numbers=False)
    #fig.savefig('ChinaItalyCFRs.pdf', transparent=True, bbox_inches='tight')

    fig = bar_chart_by_age(data_Simpson, 'cases_by_age', show_numbers=False)
    #fig.savefig('ChinaItalyCaseDemographic.pdf', transparent=True, bbox_inches='tight')