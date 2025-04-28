"""
This file contains the constants used in the package.
"""

from typing import Literal

API_KEY_LIST = [
    "sk-qxhrghwznwfqfbjwgvmsxextmsvujfysbeoygqfdtshhiftq",  # siliconflow yql
    "sk-hqsayrakspukokjtqeuokgofsevpqwyhdyxkoiezrybemdmm",  # siliconflow 137 mine,
    "sk-yylucttutrbbpadxfhpvxojogdfbbmtvyzmgvtfzlxhfmztm",  # siliconflow fjy,
    "sk-lvzzusawuybrwgsyygigcmbovllwyklguzcxzgdbkvadijpg",  # siliconflow zrt,
    "sk-zeuyoabkkqpoujthzuwyuzbwxhepbqpionulgnlisvdxseen",  # siliconflow yjz,
    "sk-xjkzyprognbbiwogaksfwejwjfpmcttkfhjetreyvhpfqsfs",  # siliconflow tcyf,
    "sk-mjrpvooaehyvlyzzujicksocihfsopeebgckfudkvyxndgnl",  # siliconflow mine,
    "sk-zuayonhuqaoiyyjxuueihsxwpuyoayehanxderyrokorhppb",  # siliconflow xfl0
]

API_MODEL_LIST = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct"   
]

# API_KEY_LIST = [
#     "sk-mjrpvooaehyvlyzzujicksocihfsopeebgckfudkvyxndgnl",  # siliconflow mine,
#     "sk-zuayonhuqaoiyyjxuueihsxwpuyoayehanxderyrokorhppb",  # siliconflow xfl0
# ] + [
#     "sk-zuayonhuqaoiyyjxuueihsxwpuyoayehanxderyrokorhppb",  # siliconflow xfl0
# ] * 10

# API_MODEL_LIST = ["meta-llama/Meta-Llama-3.1-8B-Instruct"] * 2 + ["Pro/meta-llama/Meta-Llama-3.1-8B-Instruct"] * 10


# Define the map scope of the each city
MAP_SCOPE = {
    'Chicago': [
        {
            'left_bottom': [-87.68478590505254, 41.838495667271154],
            'right_top': [-87.60719496495767, 41.91339680181598]
        }
    ],
    'SanFrancisco': [
        {
        'left_bottom': [ -122.4488372368169, 37.7447093129195],
        'right_top': [-122.37948604257284, 37.813904616832886]
        }
    ],
}

MAP_DATA_PATH = './cache/map_data_Chicago.pkl'

PLATFORM = Literal['openai', 'siliconflow', 'deepseek', 'zhipu', 'aliyun']

# Define the API key environment variables 
API_KEY_MAP = {
    'openai': 'OPENAI_API_KEY',
    'siliconflow': 'SILICONFLOW_API_KEY',
    'deepseek': 'DEEPSEEK_API_KEY',
    'zhipu': 'ZHIPU_API_KEY',
    'aliyun': 'ALIYUN_API_KEY'
}

# Define the base URL for each platform
BASE_URL_MAP = {
    'openai': None, 
    'siliconflow': 'https://api.siliconflow.cn/v1',
    'deepseek': 'https://api.deepseek.com/v1',
    'zhipu': 'https://open.bigmodel.cn/api/paas/v4/',
    'aliyun': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
}

MODEL_LIST = {
    'openai': [
        'gpt-4o-mini',  # OpenAI GPT-4o Mini
        'gpt-4o',       # OpenAI GPT-4o 
    ],
    'siliconflow': [
        "Qwen/Qwen2.5-7B-Instruct",     # free, qwen-2.5-7b-instruct
        "Pro/Qwen/Qwen2.5-7B-Instruct", # ￥0.35/ M token, qwen-2.5-7b-instruct
        "Qwen/Qwen2.5-14B-Instruct",    # ￥0.75/ M token, qwen-2.5-14b-instruct
        "Qwen/Qwen2.5-32B-Instruct",    # ￥1.26/ M token, qwen-2.5-32b-instruct
        "Qwen/Qwen2.5-72B-Instruct",    # ￥4.13/ M token, qwen-2.5-64b-instruct
        "meta-llama/Meta-Llama-3.1-8B-Instruct",  # free, meta-llama-3.1-8b-instruct
        "Pro/meta-llama/Meta-Llama-3.1-8B-Instruct", # ￥0.42/ M token, meta-llama-3.1-8b-instruct
        "meta-llama/Meta-Llama-3.1-70B-Instruct", # ￥4.13/ M token, meta-llama-3.1-70b-instruct
        "meta-llama/Meta-Llama-3.1-405B-Instruct" # ￥21.0/ M token, meta-llama-3.1-405b-instruct
        "BAAI/bge-m3",  # free, bge-m3, embedding model
        "deepseek-ai/DeepSeek-V2.5", # ￥1.33/ M token, deepseek-v2.5
    ],
    'deepseek': [
        "deepseek-chat",    # ￥1.0 / M token, deepseek-chat, cache 0.1
        "deepseek-v2.5",    # ￥1.0 / M token, deepseek-v2.5
    ],
    'zhipu': [],
    'aliyun': []
}