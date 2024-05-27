# Aguas de Gaia API

## Installation
```bash
$ pip install aguasgaia
```
## Usage
```python
import asyncio
import aiohttp
from aguasgaia import AguasGaia


async def main():
    session = aiohttp.ClientSession()

    aguas = AguasGaia(session, "<USERNAME>", "<PASSWORD>")
    print("LOGIN: ", await aguas.login())

    print("SUBSCRIPTIONS:\n{0}".format(await aguas.get_subscriptions()))

    inv = await aguas.get_last_invoice()
    print("INVOICE: {0}\n{1}".format(inv.invoice_value, inv.invoice_attributes))

    consumption = await aguas.get_last_consumption()
    print("CONSUMPTION: {0}\n{1}".format(consumption.consumption_value, consumption.consumption_attributes))

    await session.close()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
```

## Tests
Make sure pytest asyncio is installed
```bash
$ pip install pytest-asyncio
```
Execute the tests
```bash
$ pytest tests/
```