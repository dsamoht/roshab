#!/usr/bin/env python3
import argparse

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='coverm output table', required=True)
    parser.add_argument('-n','--name', help='name associated to the input table', required=True)
    return parser.parse_args()

def extract_mean(df):
    mean_cols = [col for i, col in enumerate(df.columns) if i % 3 == 0]
    return df[mean_cols].copy()

def extract_trimmed_mean(df):
    trimmed_mean_cols = [col for i, col in enumerate(df.columns) if i % 3 == 1]
    return df[trimmed_mean_cols].copy()

def extract_read_count(df):
    read_count_cols = [col for i, col in enumerate(df.columns) if i % 3 == 2]
    return df[read_count_cols].copy()

def plot_spatial(df, pdf_handle):
    dates = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in df.columns]
    sites = [i.split('_XsiteX_')[-1].split(r'.fa')[0].strip() for i in df.columns]
    sorted_columns = [col for _, col in sorted(zip(sites, df.columns), key=lambda x: x[0])]
    df = df[sorted_columns]

    df = df.T
    df['site'] = sites
    nonzero = (df.drop(columns="site") != 0).any()
    df = df.loc[:, nonzero.index[nonzero].tolist() + ["site"]]

    if len(set(dates)) > 1:
        return
    else:
        ax = df.plot(x='site',
        kind='bar',
        stacked=False,
        edgecolor='black',
        figsize=(10, 6),
        ylabel='Trimmed mean coverage',
        xlabel='Site',
        title=f'{dates[-1]} - Trimmed mean coverage of Cyanobacteria genomes (NCBI)')
        
        ax.legend(
            title='',
            bbox_to_anchor=(1.02, 0.5),
            loc='center left',
            borderaxespad=0
        )
        plt.tight_layout()
        pdf_handle.savefig()
        plt.close()

def plot_longitudinal(df, pdf_handle):
    dates = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in df.columns]
    sites = [i.split('_XsiteX_')[-1].split(r'.fa')[0].strip() for i in df.columns]
    sorted_columns = [col for _, col in sorted(zip(dates, df.columns), key=lambda x: x[0])]
    df = df[sorted_columns]

    df = df.T
    df['site'] = sites
    nonzero = (df.drop(columns="site") != 0).any()
    df = df.loc[:, nonzero.index[nonzero].tolist() + ["site"]]
    df['date'] = dates

    if len(set(dates)) > 1:
        for site in set(sites):
            site_df = df[df['site'] == site]
            ax = site_df.plot(x='date',
            kind='bar',
            stacked=False,
            edgecolor='black',
            figsize=(10, 6),
            ylabel='Trimmed mean coverage',
            xlabel='Date',
            title=f'{site} - Trimmed mean coverage of Cyanobacteria genomes (NCBI)')
        
            ax.legend(
                title='',
                bbox_to_anchor=(1.02, 0.5),
                loc='center left',
                borderaxespad=0
            )
            plt.tight_layout()
            pdf_handle.savefig()
            plt.close()
    else:
        return


def main():
    args = parse_arguments()
    df = pd.read_csv(args.input, sep='\t', header=0, index_col=0)
    df = extract_trimmed_mean(df)
    name = args.name.strip().replace(' ', '_')
    with PdfPages(f"{name}_coverm_cyano_ncbi_barplots.pdf") as pdf_out:
        plot_spatial(df, pdf_out)
        plot_longitudinal(df, pdf_out)


if __name__ == "__main__":
    main()
