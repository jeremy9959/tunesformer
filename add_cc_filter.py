import re
import os
import json
import jellyfish
from tqdm import tqdm
from unidecode import unidecode
import sys


def ld_sim(str_a, str_b):
    ld = jellyfish.levenshtein_distance(str_a, str_b)
    sim = 1 - ld / (max(len(str_a), len(str_b)))
    return sim


def num_alph(line):
    num_flag = False
    alpha_flag = False
    valid_flag = False

    for char in line:
        if char.isnumeric() and alpha_flag == False and valid_flag == False:
            return True
        elif char.isalpha() and num_flag == False:
            return False
        elif char == "(" or char == '"' or char == "!":
            valid_flag = True


def split_txt(text):
    lines = re.split("(\n)", text)
    lines = [lines[i * 2] + lines[i * 2 + 1] for i in range(int(len(lines) / 2))]
    meta_flag = False
    meta_idx = 0

    for line in lines:
        if len(line) > 1 and line[0].isalpha() and line[1] == ":":
            meta_idx += 1
            meta_flag = True
        else:
            if meta_flag:
                break
            else:
                meta_idx += 1

    meta_data = "".join(lines[:meta_idx])
    body_data = text[len(meta_data) :]

    delimiters = ":|", "||", "|]", "::", "|:", "[|"
    regexPattern = "(" + "|".join(map(re.escape, delimiters)) + ")"
    body_data = re.split(regexPattern, body_data)
    body_data = list(filter(lambda a: a != "", body_data))
    if len(body_data) == 1:
        body_data = [text[len(meta_data) :][::-1].replace("|", "]|", 1)[::-1]]
    else:
        if body_data[0] in delimiters:
            body_data[1] = body_data[0] + body_data[1]
            body_data = body_data[1:]
        body_data = [
            body_data[i * 2] + body_data[i * 2 + 1]
            for i in range(int(len(body_data) / 2))
        ]

    merged_body_data = []

    for line in body_data:
        if num_alph(line):
            try:
                merged_body_data[-1] += line
            except:
                return None, None
        else:
            merged_body_data.append(line)

    return meta_data, merged_body_data


def run_strip(line, delimiters):
    for delimiter in delimiters:
        line = line.strip(delimiter)
        line = line.replace(delimiter, "|")
    return line


def add_tokens(meta_data, merged_body_data):
    if merged_body_data == None:
        return "", ""
    delimiters = ":|", "||", "|]", "::", "|:", "[|"
    sec = len(merged_body_data)
    if sec > 8:
        return "", ""
    bars = []
    sims = []

    for line in merged_body_data:
        line = run_strip(line, delimiters)
        bars.append(line.count("|") + 1)

    for anchor_idx in range(1, len(merged_body_data)):
        sim = []
        for compar_idx in range(anchor_idx):
            sim.append(
                ld_sim(merged_body_data[anchor_idx], merged_body_data[compar_idx])
            )
        sims.append(sim)

    header = "S:" + str(sec) + "\n"
    for i in range(len(bars)):
        if i > 0:
            for j in range(len(sims[i - 1])):
                header += "E:" + str(round(sims[i - 1][j] * 10)) + "\n"
        if bars[i] > 32:
            return "", ""
        header += "B:" + str(bars[i]) + "\n"
    return unidecode(header), unidecode(meta_data + "".join(merged_body_data))


def is_one_voice(tune):

    if "V:2" in tune:
        return False
    else:
        return True


def run_filter(tune):
    score = ""
    lines = tune.split("\n")
    for line in lines:
        if (
            line[:2]
            in [
                "A:",
                "B:",
                "C:",
                "D:",
                "F:",
                "G",
                "H:",
                "N:",
                "O:",
                "R:",
                "r:",
                "S:",
                "T:",
                "V:",
                "W:",
                "w:",
                "X:",
                "Z:",
            ]
            or line == "\n"
            or line.startswith("%")
        ):
            continue
        else:
            if "%" in line:
                line = line.split("%")
                bar = line[-1]
                line = "".join(line[:-1])
                score += line + "\n"
            else:
                score += line + "\n"
    if not is_one_voice(score):
        score = ""
    return score.strip()


def add_control_codes(tune):
    tune = run_filter(tune)
    meta_data, merged_body_data = split_txt(tune)
    control_code, tune = add_tokens(meta_data, merged_body_data)
    if tune != "":
        item = {}
        item["control code"] = control_code
        item["abc notation"] = "X:1\n" + tune
    return item
