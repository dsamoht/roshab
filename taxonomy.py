"""
Usage:
1st argument [sys.argv[1]] : output file (report) from `kraken2`
2nd argument [sys.argv[2]] : output file from `bracken`
3rd argument [sys.argv[3]] : name of the .html output
"""

import sys

import pandas as pd
import plotly.express as px


kraken_out = pd.read_csv(sys.argv[1], sep="\t", header=None)
kraken_out[5] = kraken_out[5].apply(lambda x: x.strip())
kraken_out[3] = kraken_out[3].apply(lambda x: x.strip())
kraken_out_rev = kraken_out.reindex(index=kraken_out.index[::-1])
braken_out = pd.read_csv(sys.argv[2], sep="\t")

new_df = pd.DataFrame(index=[], columns=["n_reads"])

tax_to_val = {"S": 0, "G": 1, "F": 2,
              "O": 3, "C": 4, "P": 5}

def clad_finder(sp_name):

    taxa_dict = {"S": sp_name}
    start_i = kraken_out[kraken_out[5]==sp_name].index.tolist()[-1]

    for i in range(start_i, 0, -1):
        lvl = kraken_out[3][i]
        if lvl[0] not in taxa_dict and sorted([tax_to_val[tax[0]] for tax in taxa_dict])[-1] <= tax_to_val[lvl[0]]:
            taxa_dict[lvl] = kraken_out[5][i]
        if lvl == "P":
            taxa_dict[lvl] = kraken_out[5][i]
            break
        else:
            continue

    return taxa_dict

for i in range(braken_out.shape[0]):
    clad_dict = clad_finder(braken_out.loc[i, "name"])
    clad_dict["n_reads"] = braken_out.loc[i, "new_est_reads"]
    new_row = pd.DataFrame([clad_dict])
    new_df = pd.concat([new_df, new_row], ignore_index=True)

new_df = new_df.fillna("unknown")

fig = px.sunburst(new_df.assign(hole=" "), path=["hole", "P", "C", "O", "F", "G", "S"],
                  values="n_reads")
fig.update_traces(textinfo="label+percent root")
fig.write_html(sys.argv[3])
