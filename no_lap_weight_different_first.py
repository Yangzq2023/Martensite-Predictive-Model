import ast
import pandas as pd
from tqdm import tqdm
from pymatgen.core import Composition
from divide_composition_different_first import divide_composition

source_data = pd.read_excel(r"MPDB_1comp_2comp_3comp_summary_structure_operation_subgroup.xlsx")
composition_data = pd.read_excel(r"example.xlsx")
start = 0
print(start)
composition_data = composition_data.iloc[:, :]

composition_data["composition_pymatgen"] = composition_data["composition"].apply(Composition)

source_data["composition"] = source_data["composition"].apply(Composition)

# 初始化一个 DataFrame 放特征
use_columns_list = ['density', 'energy_above_hull', 'energy_per_atom', 'formation_energy_per_atom', 'lattice_a',
                    'lattice_b', 'lattice_c', 'angle_alpha', 'angle_beta', 'angle_gamma', 'volume',
                    "operation_count", 'subgroup_count']
type_list = ["_high", "_low", "_relation"]
feature_columns = []
for type_ in type_list:
    for use_columns in use_columns_list:
        feature_columns.append(use_columns+type_)
# 使用 assign() 方法创建新列，初始值为 None（或其他默认值）
composition_data = composition_data.assign(**{col: None for col in feature_columns})
# feature_space = pd.DataFrame(columns=feature_columns)

# 遍历DataFrame的每一行
for index, row_of_composition_data in tqdm(composition_data.iterrows(), total=len(composition_data)):
    composition = row_of_composition_data["composition_pymatgen"]
    result = divide_composition(composition, source_data)
    energy_high_data = result[0]
    energy_low_data = result[1]
    # print(energy_high_data)
    # print(energy_low_data)

    # 处理无法构建特征的情况
    if len(energy_high_data) == 0:
        # 创建一个只有NaN值的DataFrame，列名与df相同
        # empty_row = pd.DataFrame(columns=feature_space.columns)
        # 在df末尾添加一个空值行
        # feature_space.loc[len(feature_space)] = empty_row
        continue

    # 转换ratio列为针对总体的占比
    remaining = 100  # 初始剩余百分比
    converted_ratios = []  # 存储转换后的占比

    for ratio in energy_high_data['ratio']:
        actual_ratio = remaining * (ratio / 100)  # 计算实际占总体的百分比
        converted_ratios.append(actual_ratio)  # 添加到列表
        remaining -= actual_ratio  # 更新剩余百分比

    # 将计算结果添加到DataFrame
    energy_high_data['converted_ratio'] = converted_ratios

    # 转换ratio列为针对总体的占比
    remaining = 100  # 初始剩余百分比
    converted_ratios = []  # 存储转换后的占比

    for ratio in energy_low_data['ratio']:
        actual_ratio = remaining * (ratio / 100)  # 计算实际占总体的百分比
        converted_ratios.append(actual_ratio)  # 添加到列表
        remaining -= actual_ratio  # 更新剩余百分比

    # 将计算结果添加到DataFrame
    energy_low_data['converted_ratio'] = converted_ratios

    info_list = []
    for info in energy_high_data['subgroup_info']:
        if info == "['no_subgroup']":
            info_list.append(0)
        else:
            info_list.append(len(ast.literal_eval(info)))

    energy_high_data["subgroup_count"] = info_list

    # 将计算结果添加到DataFrame
    energy_low_data['converted_ratio'] = converted_ratios

    info_list = []
    for info in energy_low_data['subgroup_info']:
        if info == "['no_subgroup']":
            info_list.append(0)
        else:
            info_list.append(len(ast.literal_eval(info)))

    energy_low_data["subgroup_count"] = info_list

    energy_high_data.to_excel("energy_high.xlsx", index=False)
    energy_low_data.to_excel("energy_low.xlsx", index=False)

    # 提取特征
    use_columns_list = ['density', 'energy_above_hull', 'energy_per_atom', 'formation_energy_per_atom', 'lattice_a',
                        'lattice_b', 'lattice_c', 'angle_alpha', 'angle_beta', 'angle_gamma', 'volume',
                        "operation_count", 'subgroup_count']
    high_number_list = []
    low_number_list = []
    relation_number_list = []
    for use_columns in use_columns_list:
        # 高能量的非重叠加权
        high_weighted_number_list = []
        for _, row in energy_high_data.iterrows():
            weighted_number = row[use_columns] * row["converted_ratio"]
            high_weighted_number_list.append(weighted_number)
        high_weighted_number_sum = sum(high_weighted_number_list)
        high_number_list.append(high_weighted_number_sum)
        # 低能量的非重叠加权
        low_weighted_number_list = []
        for _, row in energy_low_data.iterrows():
            weighted_number = row[use_columns] * row["converted_ratio"]
            low_weighted_number_list.append(weighted_number)
        low_weighted_number_sum = sum(low_weighted_number_list)
        low_number_list.append(low_weighted_number_sum)
        relation_number = high_weighted_number_sum - low_weighted_number_sum
        relation_number_list.append(relation_number)
    composition_feature = high_number_list + low_number_list + relation_number_list
    # 使用 loc 方法将数据添加到指定行
    composition_data.loc[index, feature_columns] = composition_feature
    # feature_space.loc[len(feature_space)] = composition_feature

# print(feature_space)

# 使用pd.concat()进行左右拼接
# result = pd.concat([composition_data, feature_space], axis=1)
# 使用 drop() 方法删除指定的列
composition_data = composition_data.drop(columns=['composition_pymatgen'])
composition_data.dropna(inplace=True)
composition_data.to_excel(rf"example_feature.xlsx", index=False)
