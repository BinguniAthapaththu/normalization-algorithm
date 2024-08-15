# -*- coding: utf-8 -*-
"""Normalization_Module3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xMHPqKtLeUW9BEWPuNpR013J9Q-sxfV9
"""

import pandas as pd
import tabulate
from tabulate import tabulate
import nltk
from nltk import word_tokenize, pos_tag

def extract_dependencies(text, simple_keys):
    dependencies = []
    sentences = text.split('.')

    for sentence in sentences:
        words = word_tokenize(sentence)
        if "determines" in words or "determine" in words:
            parts = sentence.split("determines" if "determines" in words else "determine")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "uniquely identifies" in sentence or "uniquely identify" in sentence:
            parts = sentence.split("uniquely identifies" if "uniquely identifies" in sentence else "uniquely identify")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "depends on" in sentence or "depend on" in sentence:
            parts = sentence.split("depends on" if "depends on" in sentence else "depend on")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "determined by" in sentence:
            parts = sentence.split("determined by")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "there is at most one" in sentence:
            parts = sentence.split("there is at most one")
            determinant = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinant, dependents))
        elif "unique for" in sentence:
            parts = sentence.split("unique for")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "unique to" in sentence:
            parts = sentence.split("unique to")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
        elif "dependent on" in sentence:
            parts = sentence.split("dependent on")
            determinants = [word.strip() for word, pos in pos_tag(word_tokenize(parts[1])) if pos.startswith('N') and word in simple_keys]
            dependents = [word.strip() for word, pos in pos_tag(word_tokenize(parts[0])) if pos.startswith('N') and word in simple_keys]
            dependencies.append((determinants, dependents))
    return dependencies

def construct_dependency_matrix(dependencies, simple_keys):
    num_determinants = len(dependencies)
    num_simple_keys = len(simple_keys)
    dependency_matrix = [[0] * num_simple_keys for _ in range(num_determinants)]

    for i, (determinants, dependents) in enumerate(dependencies):
        determinant_set = set(determinants)
        for j, simple_key in enumerate(simple_keys):
            if simple_key in dependents:
                dependency_matrix[i][j] = 1
            if simple_key in determinant_set:
                dependency_matrix[i][j] = 2

    return dependency_matrix

def create_attribute_sets(dependencies, simple_keys, dependency_matrix):
    attribute_sets = []

    def are_lists_equal(list1, list2):
        return sorted(list1) == sorted(list2)

    keys_with_0_and_2 = []
    for j in range(len(simple_keys)):
        values = [dependency_matrix[i][j] for i in range(len(dependency_matrix))]
        if all(value in [0, 2] for value in values):
            keys_with_0_and_2.append(simple_keys[j])

    initial_set = keys_with_0_and_2
    attribute_sets.append(initial_set)

    for determinants, _ in dependencies:
        add_to_set = True
        for attr in keys_with_0_and_2:
            if attr not in determinants:
                add_to_set = False
                break
        if add_to_set:
            if not any(are_lists_equal(determinants, existing_set) for existing_set in attribute_sets):
                attribute_sets.append(determinants)
        else:
            new_set = keys_with_0_and_2 + [attr for attr in determinants if attr not in keys_with_0_and_2]
            if not any(are_lists_equal(new_set, existing_set) for existing_set in attribute_sets):
                attribute_sets.append(new_set)

    return attribute_sets

def dependency_closure_matrix(dependency_matrix, determinant_keys, simple_keys,candidate_keys):
    n = len(dependency_matrix)
    m = len(simple_keys)

    closure_matrix = [row[:] for row in dependency_matrix]

    for k in range(n):
        for i in range(n):
            if i == k or (determinant_keys[k] in candidate_keys and determinant_keys[i] in candidate_keys):
               continue
            elif all(closure_matrix[k][simple_keys.index(attr)] != 0 for attr in determinant_keys[i]):
                for j in range(m):
                    if closure_matrix[i][j] != 0 and closure_matrix[i][j] != 2:
                        if closure_matrix[i][j] == determinant_keys[k] and closure_matrix[k][j] == 1:
                           continue
                        elif closure_matrix[k][j] == 0 or closure_matrix[k][j] == 1:
                            closure_matrix[k][j] = determinant_keys[i]

    return closure_matrix

def create_attribute_closures_matrix(attribute_sets, simple_keys, dependency_matrix, dependencies):
    n = len(attribute_sets)
    m = len(simple_keys)
    attribute_closures_matrix = [[0] * m for _ in range(n)]
    primary_key = None
    candidate_keys = []

    for i, attr_set in enumerate(attribute_sets):
        for attr in attr_set:
            if attr in simple_keys:
                j = simple_keys.index(attr)
                attribute_closures_matrix[i][j] = 1

        missing_dependencies = []
        for determinants, dependents in dependencies:
            if all(attribute_closures_matrix[i][simple_keys.index(attr)] == 1 for attr in determinants):
                for j in range(m):
                    if dependency_matrix[dependencies.index((determinants, dependents))][j] == 1:
                        attribute_closures_matrix[i][j] = 1
            else:
                missing_dependencies.append((determinants, dependents))

        initial_missing_determinants = len(missing_dependencies)

        if initial_missing_determinants < len(dependencies):
            for _ in range(initial_missing_determinants):
                current_missing_determinant_keys = len(missing_dependencies)
                for determinants, dependents in missing_dependencies[:]:
                    if all(attribute_closures_matrix[i][simple_keys.index(attr)] == 1 for attr in determinants):
                        for j in range(m):
                            if dependency_matrix[dependencies.index((determinants, dependents))][j] == 1:
                                attribute_closures_matrix[i][j] = 1
                        missing_dependencies.remove((determinants, dependents))

                if current_missing_determinant_keys == len(missing_dependencies) or len(missing_dependencies) == 0:
                    break

        if all(attribute_closures_matrix[i][j] == 1 for j in range(m)):
            if i == 0:
                primary_key = attr_set
                candidate_keys.append(attr_set)
                break
            else:
                candidate_keys.append(attr_set)

    if candidate_keys:
        if len(candidate_keys) == 1:
            primary_key = candidate_keys[0]
            # candidate_keys = []
        else:
            same_length_keys = [key for key in candidate_keys if len(key) == len(candidate_keys[0])]
            if len(same_length_keys) == len(candidate_keys):
                primary_key = candidate_keys[0]
            else:
                min_length_key = min(candidate_keys, key=len)
                primary_key = min_length_key

    return attribute_closures_matrix, primary_key, candidate_keys



def generate_2NF(dependency_closure, determinant_keys, simple_keys, primary_key):
    remaining_determinant_keys = determinant_keys[:]
    remaining_simple_keys = simple_keys[:]
    dependency_matrices_in_2NF = []
    new_determinants_all_2NF = []
    new_simple_keys_all_2NF = []
    primary_keys_2NF = []

    k = 0
    while k < len(remaining_determinant_keys):
        partial_dependencies = []
        if remaining_determinant_keys[k] == primary_key:
            k += 1
            continue
        # Check conditions for partial dependency
        if (set(remaining_determinant_keys[k]).issubset(set(primary_key)) and len(remaining_determinant_keys[k]) < len(primary_key)):
            # Add determinant and its dependents with value 1 in dependency closure matrix to partial dependency list
            partial_dependencies.extend(remaining_determinant_keys[k])
            primary_keys_2NF.append(remaining_determinant_keys[k])
            current_key = remaining_determinant_keys[k]
            for j in range(len(simple_keys)):
                if dependency_closure[determinant_keys.index(remaining_determinant_keys[k])][j] == 1:
                    partial_dependencies.append(simple_keys[j])
                    if simple_keys[j] in remaining_simple_keys:
                      remaining_simple_keys.remove(simple_keys[j])
            remaining_determinant_keys.remove(remaining_determinant_keys[k])

            i = 0
            while i < len(remaining_determinant_keys):
                    if set(remaining_determinant_keys[i]).issubset(set(current_key)):
                      i += 1
                      continue
                    else:
                      determinant_key_index = determinant_keys.index(remaining_determinant_keys[i])
                      # Check if determinant_key is in partial dependencies and not the primary key
                      if all(attr in partial_dependencies for attr in remaining_determinant_keys[i]):
                          # Add dependents of determinant_key with value 1 in dependency closure matrix to partial dependencies list
                          for j in range(len(simple_keys)):
                              if dependency_closure[determinant_key_index][j] == 1:
                                  partial_dependencies.append(simple_keys[j])
                                  if simple_keys[j] in remaining_simple_keys:
                                    remaining_simple_keys.remove(simple_keys[j])
                          remaining_determinant_keys.remove(remaining_determinant_keys[i])
                          i = 0
                      else:
                        i += 1


            new_determinants = []
            new_simple_keys = []
            for key in determinant_keys:
                if set(key).issubset(set(current_key)) and len(key) < len (current_key):
                  continue
                if set(key).issubset(set(partial_dependencies)):
                    new_determinants.append(key)
            for key in simple_keys:
                if key in partial_dependencies:
                    new_simple_keys.append(key)
            new_determinants_all_2NF.append(new_determinants)
            new_simple_keys_all_2NF.append(new_simple_keys)
            new_matrix = create_new_matrix(new_determinants, new_simple_keys, dependency_closure, simple_keys, determinant_keys)
            dependency_matrices_in_2NF.append(new_matrix)


        else:
          k += 1
    if remaining_determinant_keys:
      new_determinants_all_2NF.append(remaining_determinant_keys)
      new_simple_keys_all_2NF.append(remaining_simple_keys)
      new_matrix = create_new_matrix(remaining_determinant_keys, remaining_simple_keys, dependency_closure, simple_keys, determinant_keys)
      dependency_matrices_in_2NF.append(new_matrix)
      primary_keys_2NF.append(primary_key)
    elif remaining_simple_keys :
      new_determinants2 = []
      new_determinants2.append(primary_key)
      new_determinants_all_2NF.append(new_determinants2)
      new_simple_keys_all_2NF.append(remaining_simple_keys)
      primary_keys_2NF.append(primary_key)
      new_matrix1 = [[2] * len(remaining_simple_keys) for _ in range(len(new_determinants2))]
      dependency_matrices_in_2NF.append(new_matrix1)

    return dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, primary_keys_2NF


def generate_3NF(dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, new_primary_keys, candidate_keys):
    dependency_matrices_in_3NF = []
    new_determinants_all_3NF = []
    new_simple_keys_all_3NF = []
    primary_keys_3NF = []
    determinants_copy = []

    for matrix, determinants, simple_keys, primary_key in zip(dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, new_primary_keys):
        matrix_copy= matrix
        determinants_copy = determinants.copy()
        simple_keys_copy = simple_keys.copy()
        simple_keys_to_remove = []
        determinant_keys_to_remove = []
        # print("determinants_copy", determinants_copy)
        # print()
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                found_in_new_determinants = False
                for det_list in new_determinants_all_3NF:
                    if val in det_list:
                        found_in_new_determinants = True
                        break

                if found_in_new_determinants:
                    continue
                if val not in [0, 1, 2]:
                    new_determinants = []
                    new_simple_keys = []
                    if val != primary_key and val not in candidate_keys:
                        new_simple_keys.extend(val)
                        new_determinants.append(val)
                        determinant_index = determinants.index(val)
                        for k, key_value in enumerate(matrix[determinant_index]):
                            if key_value == 1:
                                new_simple_keys.append(simple_keys[k])
                                simple_keys_to_remove.append(simple_keys[k])
                        determinant_keys_to_remove.append(val)
                        new_matrix = create_new_matrix(new_determinants, new_simple_keys, matrix_copy, simple_keys_copy, determinants_copy)
                        dependency_matrices_in_3NF.append(new_matrix)
                        new_determinants_all_3NF.append(new_determinants)
                        new_simple_keys_all_3NF.append(new_simple_keys)
                        primary_keys_3NF.append(val)

        for key in determinant_keys_to_remove:
            if key in determinants:
                determinants.remove(key)
        for key in simple_keys_to_remove:
            if key in simple_keys:
                simple_keys.remove(key)
        new_matrix = create_new_matrix(determinants, simple_keys, matrix_copy, simple_keys_copy, determinants_copy)
        dependency_matrices_in_3NF.append(new_matrix)
        primary_keys_3NF.append(primary_key)
        new_determinants_all_3NF.append(determinants)
        new_simple_keys_all_3NF.append(simple_keys)


    return dependency_matrices_in_3NF, new_determinants_all_3NF, new_simple_keys_all_3NF, primary_keys_3NF



def create_new_matrix(new_determinants, new_simple_keys, matrix, simple_keys, determinant_keys):
    num_determinants = len(new_determinants)
    num_simple_keys = len(new_simple_keys)
    new_matrix = [[0] * num_simple_keys for _ in range(num_determinants)]

    for i in range(num_determinants):
        determinant_key_index = determinant_keys.index(new_determinants[i])
        for j in range(num_simple_keys):
            simple_key_index = simple_keys.index(new_simple_keys[j])
            new_matrix[i][j] = matrix[determinant_key_index][simple_key_index]

    return new_matrix



def print_matrix(matrix, determinant_keys, simple_keys, title):
    headers = [""] + simple_keys
    rows = []
    for i, row in enumerate(matrix):
        determinant_str = ', '.join(determinant_keys[i])
        rows.append([determinant_str] + row)

    print(f"\n{title}:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def main():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    df = pd.read_excel('input_data.xlsx')

    row_index = 19
    row = df.iloc[row_index]
    text = row['Text']
    simple_keys = [key.strip() for key in row['Simple Keys'].split(',')]

    dependencies = extract_dependencies(text,simple_keys)

    dependency_matrix = construct_dependency_matrix(dependencies, simple_keys)

    attribute_sets = create_attribute_sets(dependencies, simple_keys, dependency_matrix)

    attribute_closures_matrix, primary_key, candidate_keys = create_attribute_closures_matrix(attribute_sets, simple_keys, dependency_matrix, dependencies)

    dependency_closure = dependency_closure_matrix(dependency_matrix, [det for det, dep in dependencies], simple_keys,candidate_keys)

    print_matrix(dependency_matrix, [det for det, dep in dependencies], simple_keys, "Dependency Matrix")
    print_matrix(attribute_closures_matrix, attribute_sets, simple_keys, "Attribute Closures Matrix")
    print_matrix(dependency_closure, [det for det, dep in dependencies], simple_keys, "Dependency Closure Matrix")


    print("\nPrimary Key:")
    print(primary_key)
    print("\nCandidate Keys:")
    for key in candidate_keys:
        print(key)
    print()


    dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, primary_keys_2NF = generate_2NF(dependency_closure, [det for det, dep in dependencies], simple_keys, primary_key)
    print("\n\n")
    print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\n")
    print("\nMatrices in 2NF:")
    for i, (matrix_2NF, determinants_2NF, simple_keys_2NF, primary_keys) in enumerate(zip(dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, primary_keys_2NF)):
        print_matrix(matrix_2NF, determinants_2NF, simple_keys_2NF, f"New Dependency Matrix in 2NF {i+1}")
        print(f"Primary Key: {primary_keys}\n")




    dependency_matrices_in_3NF, new_determinants_all_3NF, new_simple_keys_all_3NF, primary_keys_3NF = generate_3NF(dependency_matrices_in_2NF, new_determinants_all_2NF, new_simple_keys_all_2NF, primary_keys_2NF, candidate_keys)
    print("\n\n")
    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ")
    print("\n")
    print("\nMatrices in 3NF:")
    for i, (matrix_3NF, determinants_3NF, simple_keys_3NF, primary_keys_3NF) in enumerate(zip(dependency_matrices_in_3NF, new_determinants_all_3NF, new_simple_keys_all_3NF, primary_keys_3NF)):
        print_matrix(matrix_3NF, determinants_3NF, simple_keys_3NF, f"New Dependency Matrix in 3NF {i+1}")
        print(f"Primary Key: {primary_keys_3NF}\n")


if __name__ == "__main__":
    main()