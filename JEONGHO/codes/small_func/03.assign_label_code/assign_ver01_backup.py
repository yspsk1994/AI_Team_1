def assign_a_new_book(pick_data):
    
    #pick_data = ["신간도서명1", "작가1", "출판사1", "101", "컴퓨터"]
    ret = ""
    print(ret)
    for front in pick_data:
        ret += front[0]


    #청구기호 생성 및 부여
    # 1) xxx. &
    label = '500.'
    # 2) 작가 성씨 한글자 추출 &
    wrt_last_name = pick_data[1][0]
    #print(wrt_last_name)
    label += wrt_last_name
    #print(label)
    # 3) 작가 가운데 이름 한 글자를 숫자화 &
    wrt_mid_name = pick_data[1][1]
    #print(wrt_mid_name)
    tmp = korean_to_be_englished(wrt_mid_name)
    #print(tmp)
    s =""
    for n in tmp:
        for x in range(3):
            s += n[x]
            #print(n[x])
            x += 1
    #print(s)

    label = label + s[0] +s[1]
    #print(label)

    # 숫자화 남았음
    ch_num1 = str(CHOSUNG_LIST.index(s[0]))
    ch_num2 = str(JUNGSUNG_LIST.index(s[1]))
    label = label + ch_num1 + ch_num2
    #print(label)

    # 4) 책 제목 첫글자의 초성
    first_bookname = pick_data[0][0]
    #print(first_bookname)
    tmp = korean_to_be_englished(first_bookname)
    #print(tmp)
    s =""
    for n in tmp:
        for x in range(3):
            s += n[x]
            #print(n[x])
            x += 1

    label += s[0]
    #print(label)
    return label
