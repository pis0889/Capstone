import boto3
from decimal import Decimal

# 데이터 정의
data = {
    'device_id': '001',
    'temperature': 24.5,
    'humidity': 61.2,
    'timestamp': '2025-04-05 18:00:00'
}

# float → Decimal 변환 함수
def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(x) for x in obj]
    return obj

# DynamoDB 리소스 객체 생성
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')

# 테이블 이름은 실제 네가 만든 테이블 이름으로 수정!
table = dynamodb.Table('SensorData')

# 데이터 업로드
response = table.put_item(Item=float_to_decimal(data))
print("업로드 성공:", response)
 

 






