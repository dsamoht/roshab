#!/usr/bin/env python3
import argparse

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd


# source : https://sashamaps.net/docs/resources/20-colors/
DISTINCT_COLORS = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                   '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4',
                   '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000',
                   '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9',
                   '#000000']

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='combined (multiple samples) kraken report', required=True)
    parser.add_argument('-n','--name', help='name associated to the input report', required=True)
    return parser.parse_args()

def top_n_taxlevel_relative_to_all(df, taxa_level="p", top_n=10):
   
    tax_level_table = df.loc[[str(i) for i in df.index if str(i).split("|")[-1].startswith(f"{taxa_level}__")]]
    top_n_by_sum = tax_level_table.loc[tax_level_table.sum(axis=1).nlargest(top_n).index]

    cellular = df.loc['x__cellular_organisms'] if 'x__cellular_organisms' in df.index else 0
    viruses = df.loc['x__Viruses'] if 'x__Viruses' in df.index else 0
    others_row = (cellular + viruses) - top_n_by_sum.sum()

    result_df = pd.concat([top_n_by_sum, pd.DataFrame(others_row).T.rename(index={0: 'Others'})])
    tax_level_table = result_df / result_df.sum()
    tax_level_table.index = ["|".join([j for j in i.split("|") if "x__" not in j]) for i in tax_level_table.index]

    return tax_level_table

def top_n_taxlevel_relative_to_parent(df, parent='p__Cyanobacteriota', taxa_level='g', top_n=10):
    
    tax_level_table = df.loc[[str(i) for i in df.index if parent in str(i) and i.split("|")[-1].startswith(f"{taxa_level}")]]
    top_n_by_sum = tax_level_table.loc[tax_level_table.sum(axis=1).nlargest(top_n).index]
    others_row = tax_level_table.loc[~tax_level_table.index.isin(top_n_by_sum.index)].sum()
    result_df = pd.concat([top_n_by_sum, pd.DataFrame(others_row).T.rename(index={0: 'Others'})])
    tax_level_table = result_df / result_df.sum()
    tax_level_table.index = ["|".join([j for j in i.split("|") if "x__" not in j]) for i in tax_level_table.index]
    tax_level_table.index = [i.split(f'|{taxa_level}__')[-1] for i in tax_level_table.index]
    
    return tax_level_table

def stacked_barplot(df, pdf_handle, title=None):
    ax = df.T.plot(kind='bar',
                   figsize=(10, 6),
                   stacked=True,
                   legend=False,
                   color=DISTINCT_COLORS,
                   edgecolor='k',
                   title=title)    
    ax.set_ylabel('Relative abundance')
    ax.legend(
            title='',
            bbox_to_anchor=(1.02, 0.5),
            loc='center left',
            borderaxespad=0
    )
    for text in ax.get_legend().get_texts():
        if text.get_text() != 'Others':
            text.set_fontstyle('italic')
    plt.tight_layout()
    pdf_handle.savefig()
    plt.close()

def plot_spatial(df, pdf_handle):
    dates = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in df.columns]
    sites = [i.split('_XsiteX_')[-1].strip() for i in df.columns]
    sorted_columns = [col for _, col in sorted(zip(sites, df.columns), key=lambda x: x[0])]
    df = df[sorted_columns]
    df.columns = [i.split('_XsiteX_')[-1].strip() for i in df.columns]
    if len(set(dates)) > 1:
        return
    else:
        top_n_taxlevel_relative_to_all_df = top_n_taxlevel_relative_to_all(df)
        top_n_taxlevel_relative_to_parent_df = top_n_taxlevel_relative_to_parent(df)
        stacked_barplot(top_n_taxlevel_relative_to_all_df, pdf_handle, title=f"{dates[-1]} - Relative abundance of top 10 phyla")
        stacked_barplot(top_n_taxlevel_relative_to_parent_df, pdf_handle, title=f"{dates[-1]} - Relative abundance of top 10 genus within Cyanobacteriota phylum")

def plot_longitudinal(df, pdf_handle):
    dates = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in df.columns]
    sorted_columns = [col for _, col in sorted(zip(dates, df.columns), key=lambda x: x[0])]
    df = df[sorted_columns]
    dates = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in df.columns]
    sites = [i.split('_XsiteX_')[-1].strip() for i in df.columns]
    if len(set(dates)) > 1:
        for site in set(sites):
            site_df = df.loc[:, [col for col in df.columns if site in col]]
            site_df.columns = [i.split('_XdateX_')[-1].split('_XsiteX_')[0].strip() for i in site_df.columns]
            top_n_taxlevel_relative_to_all_df = top_n_taxlevel_relative_to_all(site_df)
            top_n_taxlevel_relative_to_parent_df = top_n_taxlevel_relative_to_parent(site_df)
            stacked_barplot(top_n_taxlevel_relative_to_all_df, pdf_handle, title=f"{site} - Relative abundance of top 10 phyla")
            stacked_barplot(top_n_taxlevel_relative_to_parent_df, pdf_handle, title=f"{site} - Relative abundance of top 10 genus within Cyanobacteriota phylum")
    else:
        return

def main():
    args = parse_arguments()
    df = pd.read_csv(args.input, sep='\t', header=0, index_col=0)
    with PdfPages("kraken_cyano_barplots.pdf") as pdf_out:
        plot_spatial(df, pdf_out)
        plot_longitudinal(df, pdf_out)
    

if __name__ == "__main__":
    main()
