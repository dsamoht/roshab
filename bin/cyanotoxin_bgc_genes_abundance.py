#!/usr/bin/env python3
import argparse

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd


def parse_arguments():

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-n','--names', nargs='+', help='formatted sample information string(s)', required=True)
    parser.add_argument('-f','--files', nargs='+', help='coverage file(s)', required=True)
    parser.add_argument('-g','--group', help='group id', required=True)

    return parser.parse_args()

def extract_mapped_reads(file_path, sample_info):
    df = pd.read_csv(file_path, sep='\t', header=0)
    toxin_counts = df['#rname'].str.extract(r'_([^_]+)$')[0]
    toxin_dict = df.groupby(toxin_counts)['numreads'].sum().to_dict()
    result = {**sample_info, **toxin_dict}
    return result

def plot_longitudinal(df, pdf_handle):
    if df['date'].nunique() > 1:
        for site in df['site'].unique():
            site_df = df[df['site'] == site]
            ax = site_df.plot(x='date',
            kind='bar',
            stacked=False,
            edgecolor='black',
            figsize=(10, 6),
            ylabel='Read counts',
            xlabel='Date',
            title=f'{site} - Reads mapped on cyanotoxin-associated genes and homologs')
            
            ax.legend(
                title='Associated cyanotoxin BGC',
                bbox_to_anchor=(1.02, 0.5),
                loc='center left',
                borderaxespad=0
            )
            plt.tight_layout()
            pdf_handle.savefig()
            plt.close()
    else:
        return

def plot_spatial(df, pdf_handle):
    if df['date'].nunique() > 1:
        return
    else:
        ax = df.plot(x='site',
        kind='bar',
        stacked=False,
        edgecolor='black',
        figsize=(10, 6),
        ylabel='Read counts',
        xlabel='Site',
        title=f'{df["date"].unique()[-1]} - Reads mapped on cyanotoxin-associated genes and homologs')
        
        ax.legend(
            title='Associated cyanotoxin BGC',
            bbox_to_anchor=(1.02, 0.5),
            loc='center left',
            borderaxespad=0
        )
        plt.tight_layout()
        pdf_handle.savefig()
        plt.close()


def main():
    args = parse_arguments()
    list_of_samples = []
    group_id = args.group.strip().replace(' ', '_')
    for i, name in enumerate(args.names):
        info_dict = {}
        info_dict['sample'] = name.split('XsampleX_')[1].split('_XdateX_')[0].strip()
        info_dict['site'] = name.split('_XsiteX_')[1].strip()
        info_dict['date'] = name.split('_XdateX_')[1].split('_XsiteX_')[0].strip()
        info_dict['group'] = args.group.strip()
        list_of_samples.append(extract_mapped_reads(args.files[i], info_dict))
    
    df = pd.DataFrame.from_dict(list_of_samples)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values("date")
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    with PdfPages(f"{group_id}_toxin_barplots.pdf") as pdf_out:
        plot_spatial(df, pdf_out)
        plot_longitudinal(df, pdf_out)

if __name__ == "__main__":
    main()
