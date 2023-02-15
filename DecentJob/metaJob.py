#############################################################
# @Time        :   2022/11/29 05:11:38
# @FileName    :   metaJob.py
# @FileDir     :   ~/project/SlurmUtils
# @Author      :   Yuxiang Luo
# @Email       :   luo.929@osu.edu
# @Software    :   VSCode
# @Organization:   Center of Weldability, The Ohio State University
# @Usage       :   #TODO: Add Usage
#############################################################

import json
from typing import Dict, List, Union
import pandas as pd
from pathlib import Path

def find_job_by_params(
    condition_dict: Dict,
    df: pd.DataFrame,
    exception: List[str] = [],
    is_exact: bool = False,
):

    result, quest = query_dataframe(
        {
            key: val
            for key, val in condition_dict.items() if key not in exception
        }, df)
    if (len(result) == 0):
        return {}

    if (is_exact):
        assert len(result) == 1, f"Query return {result} on quest {quest}"

        result = result.to_dict(orient="index")
        for key, val in result.items():
            result[key]["Index"] = key

        result_dict: Dict = result[list(result.keys())[0]]
    else:
        result_dict = result.to_dict(orient="index")

    return result_dict


def migrate_static(new_job_df: pd.DataFrame, static_dir: Path):

    for dir_path in static_dir.iterdir():
        if (dir_path.is_file()):
            continue
        with open(dir_path / "case.json", 'r') as fin:
            dir_dict = json.load(fin)

        new_keys = [key for key in new_job_df.columns if key not in dir_dict]

        multi_val_keys = [
            key for key in new_keys if len(new_job_df[key].unique()) != 1
        ]
        assert len(
            multi_val_keys
        ) == 0, f"{[[key , new_job_df[key].unique().tolist()] for key in multi_val_keys]}"

        if (len(new_keys) > 0):
            print(f"{dir_path/ 'case.json'} Found new keys {new_keys}")
            for key in new_keys:
                dir_dict[key] = new_job_df[key].unique().tolist()[0]
            print(dir_dict)
            input()
            with open(dir_path / "case.json", 'w') as fout:
                json.dump(dir_dict, fout)

        new_job_dict = find_job_by_params(
            dir_dict,
            new_job_df,
            is_exact=True,
        )
        if (len(new_job_dict) == 0):
            dir_path.rename(
                dir_path.parent /
                f"{dir_path.name}_empty".replace("_empty_empty", "_empty"))
        else:
            dir_path.rename(dir_path.parent / f"{new_job_dict['Index']}_ren")
            print(
                f"Migrating {dir_path} -> {dir_path.parent/new_job_dict['Index']}"
            )

    for dir_path in static_dir.glob("*_ren"):

        dir_path.rename(dir_path.parent / dir_path.name.replace("_ren", ""))


def query_dataframe(condition_dict: Dict, df: pd.DataFrame):
    conditions = []

    for key, val in condition_dict.items():
        # print(key, val, type(val))
        if (type(val) in [int, float, bool]):
            conditions.append(f"{key}=={val}")
        else:
            conditions.append(f"{key}==\"{val}\"")

    # print(conditions)
    # input()
    quest = " and ".join(conditions)
    # print(quest)
    # input()

    result = df.query(quest)

    return result, quest
