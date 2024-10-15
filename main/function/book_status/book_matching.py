import pandas as pd
from fuzzywuzzy import fuzz

def extract_text_from_image(ocr, image_path):
    """이미지에서 텍스트 추출"""
    result = ocr.ocr(image_path, cls=True)
    extracted_text = ""

    for line in result:
        if isinstance(line, list):
            for sub_line in line:
                if isinstance(sub_line, list) and len(sub_line) == 2:
                    _, (text, confidence) = sub_line
                    extracted_text += text + "\n"
    return extracted_text.strip()

def process_cropped_image(ocr, cropped_filename, book_list):
    """크롭된 이미지에서 텍스트 추출 후 도서 목록과 매칭"""
    extracted_text = extract_text_from_image(ocr, cropped_filename)
    
    if not extracted_text:
        return []

    full_text = ' '.join(extracted_text.split())
    matches = sorted(
        [(book, fuzz.partial_ratio(full_text, book)) for book in book_list],
        key=lambda x: x[1], reverse=True
    )
    
    return matches

def load_book_list(excel_path):
    """엑셀 파일에서 도서 목록 로드"""
    df = pd.read_excel(excel_path)
    df['combined'] = df['제목'].astype(str) + ' ' + df['저자'].astype(str) + ' ' + df['출판사'].astype(str)
    return df['combined'].tolist(), df

def collect_highest_similarity_books(all_matches, book_df):
    """각 매칭 결과에서 가장 높은 유사도를 가진 도서 정보 수집"""
    highest_books = []
    for matches in all_matches:
        if matches:
            book, _ = matches[0]
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty:
                highest_books.append(book_info.iloc[0])
    return highest_books

def save_books_to_excel(books_info, excel_path='data/current_book_list.xlsx'):
    """도서 정보를 엑셀 파일로 저장"""
    df = pd.DataFrame(books_info)
    df.drop(columns=['combined'], inplace=True, errors='ignore')
    df.to_excel(excel_path, index=False)