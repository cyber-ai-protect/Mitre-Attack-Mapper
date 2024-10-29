# Mitre-Attack-Mapper

This tool lets you parse the whole Mitre Attack in search of all TTPs larching a specific keyword.
For instance, let's say you want to have a heatmap with all ransomware related TTPs, boom you have it within seconds.

No need to manually select which Threat Actor or Campaign or Software, the tool does it for you!
The script then ensures to not have any duplicates, and build a JSON heatmap that Mitre Attack Navigator understands.

And then you can focus on other tasks.


# Installation 

pip install -r requirements


# How to use

python3 Mitre-Atrack-Mapper.py

select Enterprise.Json, choose a name for the output JSON file, pick a color in which the TTPs should be highlighted, select a keyword you want to build the heatmap for.
Run.
