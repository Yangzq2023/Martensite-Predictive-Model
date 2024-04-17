import ast
import pandas as pd
from pymatgen.core import Composition
from system_extract import get_systems
from get_max_compound_ratio import get_max_compound_ratio
from remain_composition import calculate_remaining_composition


def divide_composition(composition, source_data, energy_high_data=pd.DataFrame(), energy_low_data=pd.DataFrame()):
    # 获取元素符号列表
    element_list = [element.symbol for element in composition.elements]
    if len(element_list) == 0:
        return energy_high_data, energy_low_data
    elif len(element_list) == 1:
        system_list = element_list
    else:
        # 获取成分系统
        system_list = get_systems(element_list)
    ratio_df = pd.DataFrame()
    # 按照组元查表
    for system in system_list:
        target_material_data = source_data.iloc[source_data.index[source_data['chemical_system'] == system]]
        if len(target_material_data) == 0:
            continue

        for index, row in target_material_data.iterrows():
            compound = row["composition"]
            ratio = get_max_compound_ratio(composition, compound)
            row["ratio"] = ratio
            ratio_df = pd.concat([ratio_df, row], axis=1)
    ratio_df = ratio_df.T
    if len(ratio_df) == 0:
        return energy_high_data, energy_low_data
    # print(ratio_df[["composition", "material_id", "energy_above_hull", "subgroup_info", "ratio"]])

    # 找到有同分异构关系的化合物!!!
    ratio_df['relation'] = 0
    ratio_df.loc[ratio_df.duplicated(subset=['ratio'], keep=False), 'relation'] = 1

    system_str = ''.join(system_list)
    ratio_df.to_excel(f"{system_str}.xlsx", index=False)

    # 选取ratio>40的化合物
    compound_main = ratio_df[ratio_df["ratio"] > 40]

    # 找到有群-子群关系的化合物
    compound_main_have_subgroup = compound_main[~(compound_main["subgroup_info"] == "['no_subgroup']")]

    if len(compound_main_have_subgroup) != 0:
        # 在有子群的化合物中选择能量最高的（高对称性高能量可能为奥氏体相的主要成分）
        compound_main_have_subgroup = compound_main_have_subgroup.copy()
        compound_main_have_subgroup.sort_values(by='energy_above_hull', ascending=False, inplace=True)
        energy_high_compound = compound_main_have_subgroup.head(1)
        # 找到其子群化合物中能量最低的化合物（低对称性低能量可能为马氏体的主要成分）
        subgroup = energy_high_compound.iloc[0, energy_high_compound.columns.get_loc('subgroup_info')]
        subgroup_list = ast.literal_eval(subgroup)
        # 找到其所有子群化合物数据
        subgroup_df = compound_main[compound_main['material_id'].isin(subgroup_list)]
        # 找到子群化合物中能量最低的化合物
        subgroup_df = subgroup_df.copy()
        subgroup_df.sort_values(by='energy_above_hull', ascending=True, inplace=True)
        energy_low_compound = subgroup_df.head(1)
    else:
        # 如果没有就按照占比和能量排序
        # 为突出差异，有限使用具有同分异构关系的化合物，所以最先用relation降序排序
        # 首先按照 "ratio" 列降序排序，然后按照 "energy_above_hull" 列升序排序，第一个为占比最大能量最低的化合物
        energy_low_df = ratio_df.sort_values(by=['relation', 'ratio', 'energy_above_hull'], ascending=[False, False, True])
        energy_low_compound = energy_low_df.head(1)
        # 找到占比最大能量最高的化合物
        energy_high_df = ratio_df.sort_values(by=['relation', 'ratio', 'energy_above_hull'], ascending=[False, False, False])
        energy_high_compound = energy_high_df.head(1)

    # print(composition)
    # print(energy_low_compound[["material_id", "subgroup_info", "ratio"]])
    # print(energy_high_compound[["material_id", "subgroup_info", "ratio"]])

    # 保存数据
    energy_high_data = pd.concat([energy_high_data, energy_high_compound], ignore_index=True)
    energy_low_data = pd.concat([energy_low_data, energy_low_compound], ignore_index=True)

    # 计算剩余合金成分
    energy_high_compound_formula = energy_high_compound.iloc[0, energy_high_compound.columns.get_loc('composition')]
    # print(energy_high_compound_formula)
    current_ratio = energy_high_compound.iloc[0, energy_high_compound.columns.get_loc('ratio')]
    remain_composition = calculate_remaining_composition(composition, energy_high_compound_formula, current_ratio)
    # print(remain_composition)
    if len(remain_composition.elements) == 0:
        return energy_high_data, energy_low_data
    else:
        return divide_composition(remain_composition, source_data, energy_high_data, energy_low_data)
