from order_management import find_lis, find_books_to_move

def update_book_status(current_books, previous_books, book_df, excel_path):
    """책 상태 업데이트 및 엑셀 파일 저장"""
    updated = False

    # 사라진 책 처리: '읽는중'으로 변경
    for book in previous_books:
        if book not in current_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] not in ['대출중', '오배치']:
                book_df.loc[book_df['combined'] == book, '도서상태'] = '읽는중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '읽는중'으로 변경되었습니다.")
                updated = True

    # 새로 나타난 책 처리: '배치중'으로 변경
    for book in current_books:
        if book not in previous_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] in ['읽는중']:
                book_df.loc[book_df['combined'] == book, '도서상태'] = '배치중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '배치중'으로 변경되었습니다.")
                updated = True

    # 오배치된 책 처리
    correct_order = book_df['combined'].tolist()
    current_order = [book for book in current_books if book in correct_order]

    lis_books = find_lis(current_order, correct_order)
    books_to_move = find_books_to_move(current_order, lis_books)

    for combined in books_to_move:
        book_info = book_df[book_df['combined'] == combined]
        if not book_info.empty and book_info['도서상태'].iloc[0] not in ['대출중', '오배치']:
            book_df.loc[book_df['combined'] == combined, '도서상태'] = '오배치'
            print(f"'{book_info['제목'].iloc[0]}' 상태가 '오배치'로 변경되었습니다.")
            updated = True

    # 오배치 상태였던 책이 제대로 배치된 경우 '배치중'으로 변경
    for book in current_books:
        if book in previous_books and book not in books_to_move:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] == '오배치':
                book_df.loc[book_df['combined'] == book, '도서상태'] = '배치중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '배치중'으로 변경되었습니다.")
                updated = True

    if updated:
        # 'combined' 열 제거 후 엑셀 파일 저장
        save_df = book_df.drop(columns=['combined'])
        save_df.to_excel(excel_path, index=False)
        print(f"'{excel_path}'에 업데이트된 도서 목록이 저장되었습니다.")
        print(f"오배치된 책의 수: {len(books_to_move)}")

    return book_df