import json
from collections import defaultdict

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

palette = sns.color_palette(["mediumseagreen", "royalblue", "peru"])

with open("relevant_teams.json") as f:
    relevant_teams = json.load(f)

error_map = {
    "II": "Too late",  # "Late Stop",
    "I": "Too early",  # "Early Stop",
    "III": "Too early",  # "Early Start & Stop",
    "IV": "Too early",  # "Early Start",
    "V": "Other", # "Surround"
    "VI": "Other", # "Contained"
    "VII": "Too late",  # "Late Start",
    "VIII": "Too late",  # "Late Start & Stop",
    "X": "False positive",
    "XI": "Multiple",
    "XII": "False negative",
}
role_map = {
    "Polar_expression": "Expression",
    "Source": "Holder",
    "Target": "Target",
}
order = ["False positive", "False negative", "Multiple", "Too early", "Too late", "Other"]

data = defaultdict(list)
with open("assembled_overlap.json") as f:
    for line in f:
        line = json.loads(line)
        setting = line["mono/single"]
        if line["team"] not in relevant_teams[setting]:
            continue
        total = sum(line["errors"].values())
        for error_type in line["errors"]:
            if error_type in ("IX", "N"):  # not real errors
                continue
            value = line["errors"][error_type] / total
            if value > 0.025 or True:
                data[line["dataset"], line["mono/single"]].append(
                    {
                        "Team": line["team"],
                        "Error type": error_map[error_type],
                        "Opinion span type": role_map[line["role"]],
                        "Dataset": line["dataset"],
                        "Relative frequency": value,
                        "Absolute counts": line["errors"][error_type],
                    }
                )

# sns.set_theme(style="white", palette=None)
# sns.color_palette("husl", 9)
for dataset, monomulti in data:
    sns.set(font_scale=0.7)
    print("Scattering", dataset)
    df = pd.DataFrame(data[dataset, monomulti])
    axis = sns.scatterplot(
        data=df,
        x="Team",
        y="Relative frequency",
        hue="Opinion span type",
        style="Error type",
        palette=palette,
    )
    axis.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.autoscale()
    fig = axis.get_figure()
    fig.savefig(
        f"scatter_{dataset}_{monomulti}.pdf",
    )
    plt.clf()

    sns.set(font_scale=0.9)
    if monomulti == "monolingual":
        print("Boxing", dataset)
        axis = sns.boxplot(data=df, x="Error type", y="Relative frequency", hue="Opinion span type", order=order, palette=palette)
        axis.tick_params(axis="x", rotation=0)
        fig = axis.get_figure()
        fig.savefig(f"box_{dataset}_{monomulti}.pdf")
    plt.clf()

with open("outliers.txt", "w") as f:
    for setting in ("monolingual",):
        print("Boxing", setting)
        df = pd.DataFrame(item for (_ds, monomulti), items in data.items() for item in items if monomulti == setting)
        f.write(f"Setting: {setting}\n")
        for role in ("Holder", "Target", "Expression"):
            for etype in ("False negative", "False positive", "Multiple"):
                f.write(f"{role} :: {etype}:\n")
                f.write(str(
                    df[(df["Opinion span type"] == role) & (df["Error type"] == etype)].sort_values(by=["Relative frequency"])[-5:]
                ))
                f.write("\n")
        f.write("\n")
        axis = sns.boxplot(data=df, x="Error type", y="Relative frequency", hue="Opinion span type", order=order, palette=palette)
        axis.tick_params(axis="x", rotation=0)
        axis.set_ylim(0, 0.32)
        fig = axis.get_figure()
        fig.savefig(f"box_all_{setting}.pdf")
        plt.clf()
