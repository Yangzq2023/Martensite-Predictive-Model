def get_max_compound_ratio(alloy_comp, compound_comp):
    # 计算化合物中每种元素的原子比例
    compound_ratios = {el: compound_comp.get_atomic_fraction(el) for el in compound_comp.elements}

    # 根据合金中元素的比例，找出限制化合物最大含量的元素
    min_ratio = float('inf')
    for element, ratio in compound_ratios.items():
        if element in alloy_comp:
            # 计算合金中该元素对应的最大可能比例
            alloy_ratio = alloy_comp.get_atomic_fraction(element)
            min_ratio = min(min_ratio, alloy_ratio / ratio)

    # 计算化合物的最大可能含量
    max_percentage = min_ratio * sum(compound_ratios.values()) * 100
    return max_percentage


if __name__ == "__main__":
    from pymatgen.core import Composition
    compound = Composition("CuTi")
    alloy = Composition("CuAl")
    ratio = get_max_compound_ratio(alloy, compound)
    print(ratio)
