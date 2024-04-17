from itertools import combinations


def get_systems(element_list):

    if len(element_list) == 2:
        system_list = []
        for combo in combinations(element_list, 2):
            # Sort the elements alphabetically by their symbol and join with '-'
            sorted_combo = '-'.join(sorted(el for el in combo))
            system_list.append(sorted_combo)

    else:
        system_list_binary = []
        for combo in combinations(element_list, 2):
            # Sort the elements alphabetically by their symbol and join with '-'
            sorted_combo = '-'.join(sorted(el for el in combo))
            system_list_binary.append(sorted_combo)
        system_list_ternary = []
        for combo in combinations(element_list, 3):
            # Sort the elements alphabetically by their symbol and join with '-'
            sorted_combo = '-'.join(sorted(el for el in combo))
            system_list_ternary.append(sorted_combo)
        system_list = system_list_binary + system_list_ternary

    print(system_list)
    return system_list


if __name__ == '__main__':
    # Example usage with a chemical formula
    chemical_formula = ["Cu", "Ti", "Al"]  # You can replace this with any formula you'd like to test
    result = get_systems(chemical_formula)
    print(result)

