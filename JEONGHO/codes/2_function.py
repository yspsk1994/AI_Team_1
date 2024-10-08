# 신간 도서 기능 추가
# 0.문제 내용/입력/출력/
# 1.조건 파악
# 2.프로그램(시스템) 구성도
# 3.사용한 개념/자료구조
# 4.프로그램 특징
# 5.코드

# 0.문제 내용/입력/출력/
- 문제 내용: 신간 도서 추가 기능
- 입력: 신간 도서 구입 목록(txt / xlsx), 책장에 신간 도서 배치
- 출력: 신간 타겟 도서 



# 1.조건 파악
    - 수직 텍스트 책 제목 미포함
    
# 2.프로그램(시스템) 구성도
    0) 신간 도서 구입 목록 시스템에 입력
        - 도서명/저자/출판사/[책장/책장 내 인덱스] = [분류 기호표로 치환 가능?]
    1) 도서관에 새로 도착
    2) 신간 도서를 책장에 배치
    3) 해당 책장의 카메라가 신간 도서 객체 인식
    4) 타겟 도서 책 제목/저자명/출판사 추출
    4) (0단계에서 시스템에 입력된 신간 도서 구입 목록과)유사성 검토
    5) 타겟 도서의 정확한 정보 확정
    6) 도서관 DB에 타겟 도서 데이터 등록
    7) 분류 관련 정보는 네이버 도서 api 활용 분류 분야(ex. 과학/인문/에세이 등 파악)

# 3.사용한 개념/자료구조
구매 목록, 
# 4.프로그램 특징
# 5.코드

