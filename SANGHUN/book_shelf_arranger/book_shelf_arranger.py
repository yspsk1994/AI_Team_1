"""책의 순서가 뒤죽박죽 섞여 있는 경우에도 최단 횟수로 책을 올바른 순서로 배열하기 위해 필요한 최적의 이동을 찾는 문제""" 
"""단, 이 문제에서는 연속된 책을 밀어내며 배치하는 특징을 고려해야 하므로 일반적인 정렬 알고리즘과는 차이가 있습니다."""

"""이를 해결하기 위해, 일반적인 정렬 알고리즘보다는 최소한의 이동으로 책을 재배열하는 전략을 세워야 합니다."""
"""이 문제는 Longest Increasing Subsequence(LIS, 최장 증가 부분 수열) 문제와 유사한 방식으로 해결할 수 있습니다."""


def read_books(filename):
    """텍스트 파일에서 책의 순서를 읽어오는 함수"""
    with open(filename, 'r') as file:
        return file.read().splitlines()

def find_lis(current_order, correct_order):
    """현재 순서에서 최장 증가 부분 수열(LIS)를 찾는 함수"""
    pos_map = {book: i for i, book in enumerate(correct_order)}  # 올바른 순서에서 각 책의 위치
    transformed_order = [pos_map[book] for book in current_order]  # 현재 순서를 올바른 순서의 인덱스로 변환

    # LIS 알고리즘 적용
    lis = []
    predecessors = [-1] * len(transformed_order)
    indices = []

    for i, value in enumerate(transformed_order):
        if not lis or value > lis[-1]:
            predecessors[i] = indices[-1] if indices else -1
            lis.append(value)
            indices.append(i)
        else:
            # 이분 탐색을 통해 LIS에서 value가 들어갈 자리를 찾음
            left, right = 0, len(lis) - 1
            while left < right:
                mid = (left + right) // 2
                if lis[mid] < value:
                    left = mid + 1
                else:
                    right = mid
            lis[left] = value
            indices[left] = i
            predecessors[i] = indices[left - 1] if left > 0 else -1

    # LIS에 해당하는 책의 인덱스를 추적하여 반환
    lis_books = []
    k = indices[-1]
    while k >= 0:
        lis_books.append(current_order[k])
        k = predecessors[k]

    return lis_books[::-1]

def find_books_to_move(current_order, lis_books):
    """현재 순서에서 이동해야 할 책을 찾는 함수"""
    # LIS에 포함되지 않은 책들이 이동 대상
    lis_set = set(lis_books)
    return [book for book in current_order if book not in lis_set]

def arrange_books(current_order, correct_order):
    """최단 이동 횟수로 책을 올바른 순서로 배치하는 함수"""
    moves = 0

    # 1. 현재 순서에서 최장 증가 부분 수열(LIS)를 찾음
    lis_books = find_lis(current_order, correct_order)
    #print(f"최장 증가 부분 수열(LIS): {lis_books}\n")

    # 2. LIS에 포함되지 않은 책들을 이동
    books_to_move = find_books_to_move(current_order, lis_books)

    # 책을 하나씩 제자리에 배치
    for book in books_to_move:
        correct_position = correct_order.index(book)
        current_position = current_order.index(book)

        # 책을 제자리에 배치
        current_order.pop(current_position)
        current_order.insert(correct_position, book)
        moves += 1
        print(f"'{book}'를 {current_position}에서 {correct_position}로 이동")

    return moves

if __name__ == "__main__":
    # 파일에서 현재 책 순서와 올바른 순서를 읽어옴
    correct_order = read_books('./전체_원본_책리스트.txt')
    current_order = read_books('./책리스트_순서_셔플.txt')
    
    # 책을 올바르게 배치하는 과정
    result = arrange_books(current_order, correct_order)
    
    print(f"책을 올바른 순서로 배열하기 위해 필요한 이동 횟수는 {result}회입니다.")