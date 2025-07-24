"""Script which extracts all tag combinations from paradigm CSV files."""

import click
import pandas as pd
import json
from os.path import join as pjoin
from fstmorph.src.log import info

def get_tags(tag_list):
    """ Handle special characters """
    tag_list = ["0" if t == "NONE" else t for t in tag_list]
    return tag_list

# Can be imported into other scripts, or called from the command line via main()
def extract_tag_combinations(config_file, source_path, pre_element, pre_element_tags, post_element, post_element_tags, output_file):
    info(f"Processing configuration file {config_file}")
    config = json.load(open(config_file))
    tags = {}
    
    # Set access order
    tags["access_order"] = []
    if pre_element:
        tags["access_order"] = [pre_element] + ["Stem"]
        tags[pre_element] = pre_element_tags.split(",")
    else:
        tags["access_order"] = ["Stem"]
    if post_element:
        tags["access_order"] += [post_element]
        tags[post_element] = post_element_tags.split(",")
    tags["access_order"] += config["morph_features"]

    for feature in config["morph_features"]:
        tags[feature] = set()        
    csv_files = config["regular_csv_files"] + config["irregular_csv_files"]
    for csv_file in csv_files:
        info(f"Reading {csv_file}.csv")
        csv = pd.read_csv(pjoin(source_path, config["morphology_source_path"], f"{csv_file}.csv"),
                          keep_default_na=False)
        csv_tags = set() 
        for feature in config["morph_features"]:            
            tags[feature].update(get_tags(csv[feature]))
            csv_tags.update(get_tags(csv[feature]))
        tags[csv_file] = list(csv_tags)
    for feature in config["morph_features"]:
        tags[feature] = list(tags[feature])
    info(f"Writing output JSON file {output_file}")
    with open(output_file, "w") as f:
        json.dump(tags, f, indent=4)

@click.command()
@click.option('--config-file', required=True, help="JSON config file. E.g. verb_conf.json")
@click.option('--source-path', required=True, help="Path to the source files for the FST. E.g. your BorderLakesMorph directory")
@click.option('--pre-element', required=False, default=None, help="Name of pre-element slot. E.g. TensePreverbs")
@click.option('--pre-element-tags', required=False, help="Possible pre-element (preverb/prenoun) tags which can occur before the stem. E.g. \"PVTense/gii,PVTense/wii,PVTense/wii',0\"")
@click.option('--post-element', required=False, default=None, help="Name of post-element slot. E.g. Derivation")
@click.option('--post-element-tags', required=False, help="Possible post-element (augment/derivation) tags which can occur right after the stem E.g. \"VAI+Der/magad,VII+Aug/magad,VTA+Reflex/dizo,VTA+Reflex/di,0\"")
@click.option('--output-file', required=True, help="Output json file name")
def main(config_file, source_path, pre_element, pre_element_tags, post_element, post_element_tags, output_file):
    extract_tag_combinations(config_file, source_path, pre_element, pre_element_tags, post_element, post_element_tags, output_file)

if __name__=="__main__":
    main()
