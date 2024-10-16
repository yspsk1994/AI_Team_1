import xlrd

# xls 파일 열기
file_path = '/home/liam/workspace/virtual/10_project/book_list/xls/8.test.xls'  # xls 파일 경로
workbook = xlrd.open_workbook(file_path)

# 첫 번째 시트 열기
sheet = workbook.sheet_by_index(0)

# 시트의 모든 데이터를 출력
for row_idx in range(sheet.nrows):
    row = sheet.row_values(row_idx)
    print(row)
