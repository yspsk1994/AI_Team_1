import pandas as pd

def load_book_list(excel_path):
    df = pd.read_excel(excel_path)
    df['combined'] = df['제목'].astype(str) + ' ' + df['작가'].astype(str) + ' ' + df['출판사'].astype(str)
    return df['combined'].tolist(), df

if __name__ == "__main__":
    excel_path = '/home/liam/workspace/virtual/10_project/codes/each_func/01.switch_data/bookcase1_3.xls'
    ret = load_book_list(excel_path)
    print(ret)