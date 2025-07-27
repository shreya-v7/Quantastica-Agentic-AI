import asyncio
import traceback
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async def fetch_net_worth():
    try:
        async with streamablehttp_client("https://mcp.fi.money:8080/mcp/stream") as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.call_tool('networth:fetch_net_worth')
                networth = response.get('netWorthResponse', {})
                if networth and networth.get('totalNetWorthValue'):
                    total = networth['totalNetWorthValue']
                    print(f"Total Net Worth: {total['units']} {total['currencyCode']}")
                    for asset in networth.get('assetValues', []):
                        val = asset['value']
                        print(f"{asset['netWorthAttribute']}: {val['units']} {val['currencyCode']}")
                else:
                    print("No net worth data available. Please connect your accounts in the Fi Money app.")
                    print("Full response for debugging:", response)
    except Exception as e:
        print(f"Error fetching net worth: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(fetch_net_worth())
    except Exception as main_exc:
        print(f"Fatal error: {main_exc}")
        traceback.print_exc()