# -*- coding: utf-8 -*-
# @Time    : 2023/1/19
# @Author  : Maciel


from Pinyin2Hanzi import dag, DefaultDagParams
from pypinyin import pinyin, Style, load_single_dict


class PronunciationRetrieval:
    def __init__(self, common_file, chinese_pronunciation_file):
        self.dagparams = DefaultDagParams()
        self.common_chars = self.read_common_chars(common_file)
        self.chinese_pronunciation = self.read_chinese_pronunciation(chinese_pronunciation_file)
        self.load_common_pronunciation()
        self.common_pronunciations = self.fetch_common_pronunciations()
        
    
    def read_chinese_pronunciation(self, chinese_pronunciation_file):
        chinese_pronunciation = {}
        with open(chinese_pronunciation_file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                arr = line.split(":")[-1].strip()
                pronunciations_char_pair = arr.split("#")
                if len(pronunciations_char_pair) == 2:
                    pronunciations, char = pronunciations_char_pair
                    pronunciations = pronunciations.strip()
                    char = char.strip()
                    if char == '""':
                        continue
                    chinese_pronunciation[char] = pronunciations
        return chinese_pronunciation
                
        
    def read_common_chars(self, common_file):
        # 读取常用字
        with open(common_file, "r", encoding="utf-8") as f:
            common_chars = list(f.read().strip())
            common_chars = common_chars[1:]
        return common_chars
    
    
    def load_common_pronunciation(self):
        # 加载常用字的发音
        for char in self.common_chars:
            char_pronunciations = self.chinese_pronunciation.get(char, "")
            if char_pronunciations == "":
                continue
            load_single_dict({ord(char): char_pronunciations})
    
    
    def fetch_common_pronunciations(self):
        # 获取常用字的全部发音
        common_pronunciations = []
        for char in self.common_chars:
            char_pronunciations = self.convert_char_to_pronunciation(char)
            common_pronunciations.extend(char_pronunciations)
        common_pronunciations = list(set(common_pronunciations))
        return common_pronunciations
        
        
    def convert_pronunciation_to_char(self, pronunciation, path_num):
        # 获取该发音的topk个汉字
        results = dag(self.dagparams, [pronunciation], path_num=path_num)
        items = []
        for item in results:
            char = item.path[0]
            if char in self.common_chars:
                item_dict = {'char': char,
                            'pronuncation': pronunciation}
                items.append(item_dict)
        return items
    
    
    def convert_char_to_pronunciation(self, char):
        # 将汉字转化为拼音
        if char == "嗯":
            pronunciations = ['en']
        else:
            pronunciations = pinyin(char, style=Style.TONE3, heteronym=True)
            pronunciations = [proun[:-1] for proun in pronunciations[0]]
            pronunciations = list(set(pronunciations))
        return pronunciations
    
    
    def get_same_pronunciation_char(self, pronunciations, topk):
        # 获取同音字
        same_pronunciation_chars = []
        for pronunciation in pronunciations:
            char_items = self.convert_pronunciation_to_char(pronunciation, topk)
            same_pronunciation_chars.extend(char_items)
        return same_pronunciation_chars
    
    
    def filter_same_char(self, same_pronunciation_chars, char):
        # 过滤本体汉字
        same_pronunciation_chars = [item for item in same_pronunciation_chars if item['char'] != char]
        return same_pronunciation_chars
    
    
    def get_similar_pronunciations(self, pronunciations):
        # 获取相近拼音
        # 1. 前鼻音和后鼻音区分 (n vs ng)
        # 2. n 和 l 区分 (n vs l)
        # 3. f 和 h 区分 (f vs h)
        # 4. r 和 l 区分 (r vs l)
        # 5. s 和 sh 区分 (s vs sh)
        # 6. c 和 ch 区分 (c vs ch)
        # 7. z 和 zh 区分 (z vs zh)
        # 8. b 和 p 区分 (b vs p)
        # 9. g 和 k 区分 (g vs k)
        # 10. d 和 t 区分 (d vs t)
        similar_pronunciation = []
        for pronunciation in pronunciations:
            if "n" in pronunciation:
                # n vs ng
                sim_pron = pronunciation.replace("n", "ng")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                
                # n vs l
                sim_pron = pronunciation.replace("n", "l")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "ng" in pronunciation:
                # ng vs n
                sim_pron = pronunciation.replace("ng", "n")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "l" in pronunciation:
                # l vs n
                sim_pron = pronunciation.replace("l", "n")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                
                # l vs r
                sim_pron = pronunciation.replace("l", "r")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                
            if "f" in pronunciation:
                # f vs h
                sim_pron = pronunciation.replace("f", "h")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
            
            if "h" in pronunciation:
                # h vs f
                sim_pron = pronunciation.replace("h", "f")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "r" in pronunciation:
                # r vs l
                sim_pron = pronunciation.replace("r", "l")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
            
            if "s" in pronunciation:
                # s vs sh
                sim_pron = pronunciation.replace("s", "sh")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "sh" in pronunciation:
                # sh vs s
                sim_pron = pronunciation.replace("sh", "s")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "c" in pronunciation:
                # c vs ch
                sim_pron = pronunciation.replace("c", "ch")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "ch" in pronunciation:
                # ch vs c
                sim_pron = pronunciation.replace("ch", "c")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "z" in pronunciation:
                # z vs zh
                sim_pron = pronunciation.replace("z", "zh")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "zh" in pronunciation:
                # zh vs z
                sim_pron = pronunciation.replace("zh", "z")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "b" in pronunciation:
                # b vs p
                sim_pron = pronunciation.replace("b", "p")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "p" in pronunciation:
                # p vs b
                sim_pron = pronunciation.replace("p", "b")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "g" in pronunciation:
                # g vs k
                sim_pron = pronunciation.replace("g", "k")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "k" in pronunciation:
                # k vs g
                sim_pron = pronunciation.replace("k", "g")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "d" in pronunciation:
                # d vs t
                sim_pron = pronunciation.replace("d", "t")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
                    
            if "t" in pronunciation:
                # t vs d
                sim_pron = pronunciation.replace("t", "d")
                if sim_pron in self.common_pronunciations:
                    similar_pronunciation.append(sim_pron)
        return similar_pronunciation
                
    
if __name__ == "__main__":
    common_file = "../data/chinese_3500.txt"
    chinese_pronunciation_file = "../data/chinese_pronunciation.txt"
    pronunciation_retrieval = PronunciationRetrieval(common_file, chinese_pronunciation_file)
    
    char = "吵"
    same_topk = 20
    pronunciations = pronunciation_retrieval.convert_char_to_pronunciation(char)
    print(pronunciations)
    
    # same_pronunciation_chars = pronunciation_retrieval.get_same_pronunciation_char(pronunciations, same_topk)
    # same_pronunciation_chars = pronunciation_retrieval.filter_same_char(same_pronunciation_chars, char)
    # print(same_pronunciation_chars)
    
    # similar_pronunciations = pronunciation_retrieval.get_similar_pronunciations(pronunciations)    
    # similar_topk = 10
    # similar_pronunciation_chars = pronunciation_retrieval.get_same_pronunciation_char(similar_pronunciations, similar_topk)
    # print(similar_pronunciation_chars)