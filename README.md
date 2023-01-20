# Confused_Chinese
#### 主要功能

获取混淆汉字，包括同音字、近音字和近形字。



#### 算法思想

1. 同音字

   1）获取当前汉字的拼音（包括多音字）。

   2）输出每个发音的前m个汉字，并过滤掉本体汉字。

2. 近音字

​		1）构建发音易混淆的拼音映射字典。

| 音素 | 混淆音素 |
| ---- | -------- |
| n    | ng       |
| n    | l        |
| f    | h        |
| r    | l        |
| s    | sh       |
| c    | ch       |
| z    | zh       |
| b    | p        |
| g    | k        |
| d    | t        |

​		2）根据当前发音，替换混淆音素，若存在于常见中文发音中，则考虑为近似音。

​		3）输出近似音的前n个汉字。（如果能拿到输入法的结果，效果更佳，若开源数据到时候再优化）。

3. 近形字

   1）将每个汉字转化为字体图片，可以使用不同字体风格，本项目使用中易楷体（simkai）。

   2）使用图像比较预训练模型获取每个图片的表征。

   3）根据表征计算汉字之间的相似度，并获取前k个相似的汉字作为近形字。



#### 自定义常用词

1. 我们使用了常用的3500词汉字，来源于[中文常用3500词](https://github.com/kaienfr/Font/blob/master/learnfiles/%E5%B8%B8%E7%94%A8%E6%B1%89%E5%AD%97%E5%BA%93%203500.txt)。在此基础上已经跑出一份中文混淆词映射表，在data目录下。

2. 如果读者提供自己的词典，可以使用以下脚本。

   ```
   # 生成每个汉字的字体图片
   python3 convert_char_to_font.py $your_dictionary_path$
   
   # 获取每个汉字的混淆字
   python3 fetching.py --font_dir $your char font directory$ --common_char_file $your chinese common char file path$ --pretrained $Chinese CLIP pretrained model$
   ```

3. 预训练图像模型使用阿里预训练的图文相似对比模型，可用的有以下三种。

   | 预训练图文相似对比模型名称                 |
   | ------------------------------------------ |
   | **OFA-Sys/chinese-clip-vit-base-patch16**  |
   | **OFA-Sys/chinese-clip-vit-large-patch14** |
   | **OFA-Sys/chinese-clip-vit-huge-patch14*** |

