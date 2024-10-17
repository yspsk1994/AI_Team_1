import pandas as pd

def read_books_from_excel(filename):
    """엑셀 파일에서 책 정보를 읽어오는 함수"""
    return pd.read_excel(filename)

def find_lis(current_order, correct_order):
    """현재 순서에서 최장 증가 부분 수열(LIS)를 찾는 함수"""
    pos_map = {book: i for i, book in enumerate(correct_order)}
    transformed_order = [pos_map[book] for book in current_order]

    lis = []
    predecessors = [-1] * len(transformed_order)
    indices = []

    for i, value in enumerate(transformed_order):
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
    k = indices[-1]
    while k >= 0:
        lis_books.append(current_order[k])
        k = predecessors[k]

    return lis_books[::-1]

def find_books_to_move(current_order, lis_books):
    """현재 순서에서 이동해야 할 책을 찾는 함수"""
    lis_set = set(lis_books)
    return [book for book in current_order if book not in lis_set]

def mark_misplaced_books(correct_df, current_df):
    """이동해야 할 책들을 표시하는 함수"""
    correct_order = correct_df['제목'].tolist()
    current_order = current_df['제목'].tolist()
    
    lis_books = find_lis(current_order, correct_order)
    books_to_move = find_books_to_move(current_order, lis_books)

    # '도서상태' 열이 없으면 생성
    if '도서상태' not in correct_df.columns:
        correct_df['도서상태'] = ''

    # 이동해야 할 책들의 '도서상태'를 '오배치'로 표시
    correct_df.loc[correct_df['제목'].isin(books_to_move), '도서상태'] = '오배치'

    return correct_df, len(books_to_move)

if __name__ == "__main__":
    total_book_list = 'total_book_list.xlsx'
    current_book_list = 'current_book_list.xlsx'

    correct_order_df = read_books_from_excel(total_book_list)
    current_order_df = read_books_from_excel(current_book_list)

    result_df, misplaced_count = mark_misplaced_books(correct_order_df, current_order_df)
    
    print(f"오배치된 책의 수: {misplaced_count}")
    
    # 결과를 원본 엑셀 파일에 저장
    result_df.to_excel(total_book_list, index=False)
    print(f"결과가 '{total_book_list}' 파일에 저장되었습니다.")