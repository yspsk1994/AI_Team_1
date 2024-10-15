def find_lis(current_order, correct_order):
    """현재 순서에서 최장 증가 부분 수열(LIS)를 찾는 함수"""
    pos_map = {book: i for i, book in enumerate(correct_order)}
    transformed_order = [pos_map.get(book, -1) for book in current_order if book in pos_map]

    lis = []
    predecessors = [-1] * len(transformed_order)
    indices = []

    for i, value in enumerate(transformed_order):
        if value == -1:
            continue
        if not lis or value > lis[-1]:
            predecessors[i] = indices[-1] if indices else -1
            lis.append(value)
            indices.append(i)
        else:
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

    lis_books = []
    k = indices[-1] if indices else -1
    while k >= 0:
        lis_books.append(current_order[k])
        k = predecessors[k]

    return lis_books[::-1]

def find_books_to_move(current_order, lis_books):
    """현재 순서에서 이동해야 할 책을 찾는 함수"""
    lis_set = set(lis_books)
    return [book for book in current_order if book not in lis_set]