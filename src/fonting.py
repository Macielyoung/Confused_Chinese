# -*- coding: utf-8 -*-
# @Time    : 2023/1/19
# @Author  : Maciel

from transformers import ChineseCLIPProcessor, ChineseCLIPModel
from PIL import Image
import torch
import os
import faiss
import numpy as np
os.environ['CUDA_VISIBLE_DEVICES'] = "1"


class CharRetrieval:
    def __init__(self, chars_image_dir, pretrained, device):
        self.char_image_dict = self.get_char_image_path(chars_image_dir)
        self.model, self.processor = self.load_chinese_model_processor(pretrained)
        self.device = device
        self.model = self.model.to(device)
        self.id2char = None
        self.vecs = None
        self.ids = None
        self.index = None

        
    def get_char_image_path(self, chars_image_dir):
        # 获取当前汉字的图片路径
        char_image_dict = {}
        for img in os.listdir(chars_image_dir):
            if img.endswith("png"):
                font = img.split("/")[-1][:-4]
                image_path = "../fonts/{}".format(img)
                char_image_dict[font] = image_path
        return char_image_dict
                
    
    def load_chinese_model_processor(self, pretrained):
        # 加载图像比较模型
        model = ChineseCLIPModel.from_pretrained(pretrained)
        processor = ChineseCLIPProcessor.from_pretrained(pretrained)
        return model, processor
    
    
    def get_img_features(self, image_path):
        # 获取图片表征
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)  # normalize
        return image_features
    
    
    def encode_all_chars(self):
        # 编码所有常用汉字
        all_chars = []
        all_ids = []
        all_vecs = []
        for idx, (key, value) in enumerate(self.char_image_dict.items()):
            all_chars.append(key)
            all_ids.append(idx)
            char_feature = self.get_img_features(value)
            all_vecs.append(char_feature.cpu())
            if idx % 1000 == 0:
                print("idx: {}, encode done, feature shape: {}".format(idx, char_feature.shape))
        all_vecs = torch.cat(all_vecs, 0).numpy()
        id2char = {idx: text for idx, text in zip(all_ids, all_chars)}
        self.id2char = id2char
        self.vecs = all_vecs
        self.ids = np.array(all_ids, dtype="int64")
    
    
    def build_index(self, nlist=16):
        # 针对所有汉字表征构建索引
        dim = self.vecs.shape[1]
        quant = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quant, dim, min(nlist, self.vecs.shape[0]), faiss.METRIC_INNER_PRODUCT)
        index.train(self.vecs)
        index.add_with_ids(self.vecs, self.ids)
        self.index = index
        
        
    def fetch_similar_chars(self, char, topK=10):
        # 查询字形相似的汉字
        sim_chars = []
        if char in self.char_image_dict:
            char_image_path = self.char_image_dict[char]
            vec = self.get_img_features(char_image_path)
            vec = vec.cpu().numpy()
            sim_dis, sim_idx = self.index.search(vec, topK)
            for i in range(sim_idx.shape[1]):
                idx = sim_idx[0, i]
                dis = sim_dis[0, i]
                dis = round(float(dis), 4)
                if idx not in self.id2char:
                    print("char: {}, idx: {}".format(char, idx))
                elif self.id2char[idx] == char:
                    pass
                else:
                    sim_chars.append([self.id2char[idx], dis])
        else:
            print("your input char is not in our dictionary!")
        return sim_chars
    
    
    def filter_threshold_chars(self, sim_chars, threshold):
        # 过滤阈值以下的汉字
        sim_chars = [{'char': pair[0], 'similarity': pair[1]} for pair in sim_chars if pair[1] if pair[1] >= threshold]
        return sim_chars
    
    
if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    chars_image_dir = "../fonts"
    pretrained = "OFA-Sys/chinese-clip-vit-large-patch14-336px"
    char_retrieval = CharRetrieval(chars_image_dir, pretrained, device)
    print("load char retrieval done!")
    
    # encode all char to vectors
    char_retrieval.encode_all_chars()
    print("encode all chars done!")
    
    # build faiss index
    char_retrieval.build_index(nlist=16)
    char_retrieval.index.nprob = 20
    print("build index done!")
    
    threshold = 0.95
    while True:
        input_char = input("input your char:\n")
        similar_chars = char_retrieval.fetch_similar_chars(input_char)
        similar_chars = char_retrieval.filter_threshold_chars(similar_chars, threshold)
        print(similar_chars)