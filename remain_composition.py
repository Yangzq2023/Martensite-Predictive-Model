from pymatgen.core import Composition


def calculate_remaining_composition(alloy_formula, compound_formula, compound_ratio):
    # 使用 Composition 类解析化学式
    alloy_composition = Composition(alloy_formula)
    compound_composition = Composition(compound_formula)

    # 计算化合物中各元素的元素数量
    compound_elements_count = {element: compound_composition[element] for element in compound_composition}

    # 计算化合物中各元素的比例
    compound_elements_ratio = {element: count / compound_composition.num_atoms for element, count in
                               compound_elements_count.items()}

    # 计算剩余元素的数量，确保至少有一个元素的数量大于零
    remaining_elements_count = {
        element: max(0, alloy_composition[element] - compound_ratio / 100 * ratio * alloy_composition.num_atoms)
        for element, ratio in compound_elements_ratio.items()
    }

    # 确保包含合金中可能缺失的元素
    for element in alloy_composition:
        if element not in remaining_elements_count:
            remaining_elements_count[element] = alloy_composition[element]

    # 创建新的 Composition 对象
    remaining_composition = Composition(remaining_elements_count)

    return remaining_composition


if __name__ == "__main__":
    # 示例用法
    alloy_formula = "Cu43.14Al9.4"
    compound_formula = "Al4Cu16"
    compound_ratio = 47

    result = calculate_remaining_composition(alloy_formula, compound_formula, compound_ratio)
    print(result)
    if len(result.elements) == 0:
        print("finish")
