"""
Label    Rarity    Contract    Type    TokenId
Honeypot 1    500    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    97
Honeypot 2    500    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    98
Honeypot 3    100    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    99
Honeypot 4    100    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    100
Honeypot 5    10    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    101
Honeypot 6    10    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Partner    102
Diamond Hands 1    200    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Collab    205
Diamond Hands 2    50    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Collab    206
Diamond Hands 3    10    0xe4605d46fd0b3f8329d936a8b258d69276cba264    Collab    208
Jersey    200    0xe1e546e25a5ed890dff8b8d005537c0d373497f8    Badger    1
"""
import math
import json
from typing import Iterable
from assistant.subgraph.client import fetch_nfts
from rich.console import Console
from helpers.google_sheets import fetch_sheet_data

console = Console()

NFT_SHEET_ID = "1tLRI7Bk7d4d1mCYGxoI6uIFvj1eA8-9jhCXvgXxWiDA"

MAX_NFT_BOOST = float(fetch_sheet_data(NFT_SHEET_ID, "H2:I2")[0][1].strip("%")) / 100


def build_dict(data: Iterable[Iterable[str]], name: str, key_idx: int, data_idx: int):
    filtered_data = [row for row in data if name in row[0]]
    dict = {}
    for row in filtered_data:
        dict[row[key_idx]] = row[data_idx]
    return dict


def nft_metadata(spreadsheet_id: str, spreadsheet_name: str):
    sheet_data = fetch_sheet_data(spreadsheet_id, spreadsheet_name)
    honeypot_rarity = build_dict(sheet_data, "Honeypot", 4, 1)
    diamond_hands_rarity = build_dict(sheet_data, "Diamond Hands", 4, 1)
    jersey_rarity = build_dict(sheet_data, "Jersey", 4, 1)
    memeAddress = next(filter(lambda row: "Honeypot" in row[0], sheet_data), None)[2]
    badgerNftAddress = next(filter(lambda row: "Jersey" in row[0], sheet_data), None)[2]
    return (
        honeypot_rarity,
        diamond_hands_rarity,
        jersey_rarity,
        memeAddress,
        badgerNftAddress,
    )


(
    honeypot_rarity,
    diamond_hands_rarity,
    jersey_rarity,
    memeAddress,
    badgerNftAddress,
) = nft_metadata(NFT_SHEET_ID, "A5:J14")


score_multipliers = build_dict(fetch_sheet_data(NFT_SHEET_ID, "D1:F3"), "", 0, 2)


def calc_total_nfts_score(rarities, multiplier_type):
    return sum(
        [
            calc_score(int(k), score_multipliers[multiplier_type])
            for k in rarities.values()
        ]
    )


def calc_nft_multipliers(block):
    users = fetch_nfts(block)
    userScores = {}
    userNfts = {}
    nftMultipliers = {}
    for user in users:
        addr = user["id"]
        nfts = user["tokens"]
        sumScores = 0
        userNfts[addr] = []
        for nft in nfts:
            score = calc_nft_score(nft)
            if score > 0:
                sumScores += score
                userNfts[addr].append(nft)

        if sumScores == 0:
            continue
        else:
            userScores[addr] = sumScores

    totalHoneypotScore = calc_total_nfts_score(honeypot_rarity, "Partner")
    totalDiamondScore = calc_total_nfts_score(diamond_hands_rarity, "Collab")
    totalJerseyScore = calc_total_nfts_score(jersey_rarity, "Badger")
    maxScore = totalJerseyScore + totalHoneypotScore + totalDiamondScore
    console.log("Max NFT score: {}".format((maxScore)))

    for addr, score in userScores.items():
        mult = (score / maxScore * 0.5) + 1
        nftMultipliers[addr] = {
            "score": score,
            "multiplier": mult,
            "nfts": userNfts[addr],
        }

    return nftMultipliers


def calc_nft_score(nft):
    tokenId = int(nft["token"]["tokenId"])
    nftAddress = nft["token"]["id"].split("-")[0]
    if nftAddress == memeAddress:
        if tokenId in honeypot_rarity.keys():
            return honeypot_score(nft)
        elif tokenId in diamond_hands_rarity.keys():
            return diamond_hands_score(nft)
    if nftAddress == badgerNftAddress:
        if tokenId in jersey_rarity.keys():
            return jersey_score(nft)
    return 0


def calc_score(rarity, multiplier):
    exponent = 1 / multiplier
    denom = math.pow(math.sqrt(rarity), exponent)
    return 1000 / denom


def honeypot_score(honeypot_nft):
    tokenId = int(honeypot_nft["token"]["tokenId"])
    return calc_score(honeypot_rarity[tokenId], score_multipliers["Partner"])


def diamond_hands_score(diamond_hand_nft):
    tokenId = int(diamond_hand_nft["token"]["tokenId"])
    return calc_score(diamond_hands_rarity[tokenId], score_multipliers["Collab"])


def jersey_score(jersey_nft):
    tokenId = int(jersey_nft["token"]["tokenId"])
    return calc_score(jersey_rarity[tokenId], score_multipliers["Badger"])