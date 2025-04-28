# 基于智能体的犯罪行为模拟系统

本项目实现了一个基于llm agent的crime simulation系统。系统模拟了resident、criminal、police三类agent，通过在CBG级别建模agent的移动行为和criminal agent的犯罪行为，形成城市犯罪热点的预测机制模型。

map_data_Chicago.pkl体积过大无法上传，请于此处获取并放置在cache文件夹下：https://cloud.tsinghua.edu.cn/d/14e43ba3e07941aaba76/

## 项目结构

```
│   │    ├── crime.py     # 犯罪决策模型
│   │    ├── crime.py     # 犯罪决策模型
├── agent_initialization/    # 智能体初始化数据和脚本
│   ├── citizens.json       # resident agent初始化数据
│   ├── HRIs.json          # criminal agent初始化数据
│   ├── police_agents.json  # police agent初始化数据
│   ├── citizens_initialization.py # resident agent初始化脚本
│   ├── HRI_initialization.py # criminal agent初始化脚本
│   ├── police_initialization.py # police agent初始化脚本
│   └── district/          # 区域特定数据
├── cache/                  # 缓存数据文件
├── config/                 # 配置文件
├── logs/                   # 模拟日志
├── results_safety_*/       # 模拟结果
├── src/                    # 源代码
│   ├── agents/            # 智能体类实现
│   ├── environment/       # 环境模拟
│   │   └── map.py         # 地图环境建模
│   ├── models/           # 决策模型
│   │    ├── EPR.py       # 移动算法
│   │    ├── crime.py     # 犯罪决策模型
│   │    ├── prompt_llm.py # 实验组3prompt
│   │    ├── prompt_static.py # 实验组4prompt
│   │    ├── prompt_description.py # 实验组5prompt
│   │    └── prompt_safety.py # 实验组6prompt
│   └── utils/            # llm函数
└── main.py               # 主模拟脚本
```

## 配置

系统可以通过 `config/config.yaml`进行配置。主要配置选项包括：

- 模拟参数
- 环境设置
- LLM模型设置
- 城市特定参数

## 运行模拟

运行模拟的命令：

```bash
python main.py
```

模拟将执行以下步骤：

1. 根据提供的json数据初始化智能体
2. 使用EPR模型更新智能体位置
3. 检查犯罪机会
4. 记录轨迹和犯罪事件
5. 将结果保存到结果目录
6. 重复第2步开始的进程直到完成全部step

## 复现

主要更改：

src/models/EPR.py：移动逻辑

src/models/crime.py：犯罪逻辑

## 输出

模拟系统生成以下几类输出：

- （JSON格式）智能体轨迹（"trajectories/{agent_id}.json"）
- （JSON格式）智能体访问过的CBG及访问次数（"visited/{agent_id}.json"）
- （JSON格式）个人犯罪记录（"individual_records/{agent.id}_records.json"）

结果保存在 `results_safety_YYYYMMDD`目录中。
