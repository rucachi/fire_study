import re

q = """62. 무선통신보조설비 무선기기 접속단자의 설치기준 중 다음 ( 
) 안에 알맞은 것은?
    
    ① ㉠ 500, ㉡ 5
② ㉠ 500, ㉡ 3
    ❸ ㉠ 300, ㉡ 5
④ ㉠ 300, ㉡ 3"""

match = re.search(r'\n\s*[①❶]', q)
if match:
    idx = match.start()
    new_q = q[:idx] + "\n\n[조건 삽입]\n\n" + q[idx:]
    print("MATCHED!")
    print(new_q)
else:
    print("NO MATCH")
