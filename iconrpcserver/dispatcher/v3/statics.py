from iconrpcserver.utils.icon_service import response_to_json_query
from iconrpcserver.utils.json_rpc import get_icon_stub_by_channel_name


async def statics_call(context: dict, ip: str, params: dict):
    channel = context.get('channel')
    score_stub = get_icon_stub_by_channel_name(channel)
    response = await score_stub.async_task().statics_call(ip=ip, params=params)
    return response_to_json_query(response)
