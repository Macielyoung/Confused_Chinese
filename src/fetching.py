# -*- coding: utf-8 -*-
# @Time    : 2023/1/20
# @Author  : Maciel


from fonting import CharRetrieval
from pronuncing import PronunciationRetrieval
import json
import torch
import argparse


Same_Pronunciation_topk = 20
Similar_Pronunciation_topk = 10
Same_Font_topk = 15
Similar_Font_threshold = 0.95


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--font_dir", type=str, default="../fonts", help="char font directory")
    parser.add_argument("--common_char_file", type=str, default="../data/chinese_3500.txt", help="chinese char file")
    parser.add_argument("--chinese_pronunciation_file", type=str, default="../data/chinese_pronunciation.txt", help="chinese pronunciation file")
    parser.add_argument("--pretrained", type=str, default="OFA-Sys/chinese-clip-vit-huge-patch14", help="Chinese CLIP pretrained model")
    parser.add_argument("--save_path", type=str, default="../data/confused_chinese.json", help="confused char dict save path")
    args = parser.parse_args()
    return args

    
def fetch_confused_chars(pronunciation_retrieval, char_retrieval):
    confused_char_dict = {}
    for idx, char in enumerate(pronunciation_retrieval.common_chars):
        
        pronunciations = pronunciation_retrieval.convert_char_to_pronunciation(char)
        # 获取同音字
        same_pronunciation_chars = pronunciation_retrieval.get_same_pronunciation_char(pronunciations, Same_Pronunciation_topk)
        same_pronunciation_chars = pronunciation_retrieval.filter_same_char(same_pronunciation_chars, char)
        
        # 获取发音容易混淆的字
        similar_pronunciations = pronunciation_retrieval.get_similar_pronunciations(pronunciations)
        similar_pronunciation_chars = pronunciation_retrieval.get_same_pronunciation_char(similar_pronunciations, Similar_Pronunciation_topk)
        
        # 获取形近字
        similar_font_chars = char_retrieval.fetch_similar_chars(char)
        similar_font_chars = char_retrieval.filter_threshold_chars(similar_font_chars, Similar_Font_threshold)
        
        item = {"pronunciations": pronunciations,
                "same_pronunciation_chars": same_pronunciation_chars,
                "similar_pronunciations": similar_pronunciations,
                "similar_pronunciation_chars": similar_pronunciation_chars,
                "similar_font_chars": similar_font_chars}
        if idx % 100 == 0:
            print("idx: {}, char: {}, item: {}".format(idx, char, item))

        confused_char_dict[char] = item
    return confused_char_dict


def save_confused_chars(confused_char_dict, confused_char_path):
    confused_char_json = json.dumps(confused_char_dict, ensure_ascii=False)
    with open(confused_char_path, 'w') as f:
        f.write(confused_char_json)


if __name__ == "__main__":
    args = parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    pronunciation_retrieval = PronunciationRetrieval(args.common_char_file, args.chinese_pronunciation_file)
    print("load pronunciation retrieval done!")
    
    char_retrieval = CharRetrieval(args.font_dir, args.pretrained, device)
    print("load char retrieval done!")

    # encode all char to vectors
    char_retrieval.encode_all_chars()
    print("encode all chars done!")

    # build faiss index
    char_retrieval.build_index(nlist=16)
    char_retrieval.index.nprob = 20
    print("build index done!")
    
    confused_char_dict = fetch_confused_chars(pronunciation_retrieval, char_retrieval)
    # confused_char_path = "../data/confused_chinese.json"
    save_confused_chars(confused_char_dict, args.save_path)