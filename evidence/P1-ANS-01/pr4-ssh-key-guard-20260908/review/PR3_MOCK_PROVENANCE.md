# PR3 모의시험 변수 출처
이전 로컬 시험 코드를 현재 작업 공간에서 확인한 작성 측 기록이다. PR #4 서버에서 모의시험이 활성화됐다는 기록이 아니다. 실제 서버 검증에 사용한 프로그램과 구분한다.

## pr3_review/run_review_checks.py
SHA-256: `eaf389f76860184044663e6b3241104d2ffe2ba203f8c7651431eb1ef08bae73`
```text
37:     mock_env = {'PR3_REVIEW_MOCK': '1', 'PR3_REVIEW_CASE': case,
38:                 'PR3_REVIEW_TRACE': str(trace), 'PYTHONPATH': str(root / 'mocks')}
```

## pr3_review/mocks/sitecustomize.py
SHA-256: `c1cc2332aadd8ab0d23da21c94e2f157e6ae65b59828fb0e49d013ecf4b39826`
```text
4: if os.environ.get('PR3_REVIEW_MOCK') == '1':
16:         case = os.environ['PR3_REVIEW_CASE']
18:         with open(os.environ['PR3_REVIEW_TRACE'], 'a') as f:
74:     ActionBase._execute_module = mocked_execute
```
